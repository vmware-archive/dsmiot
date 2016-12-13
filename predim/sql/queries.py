
"""
Collection of SQL snippets to retrieve model results
May-2015: Rashmi Raghu <rraghu@pivotal.io>
June-2015: Srivatsan Ramanujam <sramanujam@pivotal.io> - Ported SQL snippets into python functions + added snippets to populate heatmap & time series plots
"""

def extract_predictions_for_heatmap(input_schema, input_table):
    """
        Inputs:
        =======
        input_schema (str): The schema containing the input table
        input_table (str): The table in the input_schema containing data from the wells
        Outputs:
        ========
        A sql code block
    """
    sql = """
        select
            well_id,
            run_id as latest_run,
            ts_utc_date as latest_date,
            hour,
            prob
        from
        (
            select
                well_id,
                run_id,
                window_id,
                rank() over(partition by well_id order by run_id desc) as run_rank,
                ts_utc::date as ts_utc_date,
                extract(hour from ts_utc) as hour,
                rank() over(partition by well_id, run_id order by ts_utc::date) as ts_utc_date_rank,
                rank() over(partition by well_id, run_id, ts_utc::date, extract(hour from ts_utc) order by ts_utc) as ts_utc_hour_rank,
                ts_utc,
                prob
            from
                {input_schema}.{input_table}
        ) q
        where
            run_rank = 1 and
            ts_utc_date_rank = 1 and
            ts_utc_hour_rank = 1
        order by well_id, latest_run, latest_date, hour
    """.format(
        input_schema=input_schema,
        input_table=input_table,
    )
    return sql

def extract_features_for_tseries(input_schema, input_table, well_id, hour_of_day):
    """
        Inputs:
        =======
        input_schema (str): The schema containing the input table
        input_table (str): The table in the input_schema containing data from the wells
        well_id (long): The id of the well for which the features are being extracted
        hour_of_day (int): The hour of day (ranges from 0 to 23) for which features are sought
        Outputs:
        ========
        A sql code block
    """
    sql = """
        select
            *
        from
        (
            select
                *,
                -- we want the feature values for the last available day, for the given (well_id, hour)
                rank() over (partition by well_id order by ts_utc::date desc) as dt_rank
            from
                {input_schema}.{input_table}
            where
                well_id = {well_id} and
                extract(hour from ts_utc) = {hour_of_day}
        )q
        where
            dt_rank=1
        order by
            ts_utc;
    """.format(
        input_schema=input_schema,
        input_table=input_table,
        well_id=well_id,
        hour_of_day=hour_of_day
    )
    return sql

def extract_model_coefficients(input_schema, input_table):
    """
        Inputs:
        =======
        input_schema (str): The schema containing the input table
        input_table (str): The table in the input_schema containing data from the wells
        Outputs:
        ========
        SQL code block
    """
    #Hard-coding these feature names for now, until we can pull it out of the prediction table itself
    count_arr_names = ['depth_count', 'rpm_count', 'rop_count', 'wob_count', 'flow_count', 'bitpos_count']
    depth_stats_arr_names = ['depth_avg', 'depth_stddev', 'depth_min', 'depth_max', '(depth_max - depth_min) / depth_count']
    rpm_stats_arr_names = ['rpm_avg', 'rpm_stddev', 'rpm_min', 'rpm_max', '(rpm_max - rpm_min) /rpm_count']
    rop_stats_arr_names = ['rop_avg', 'rop_stddev', 'rop_min', 'rop_max', '(rop_max - rop_min) / rop_count']
    wob_stats_arr_names = ['wob_avg', 'wob_stddev', 'wob_min', 'wob_max', '(wob_max - wob_min) / wob_count']
    flow_stats_arr_names = ['flow_avg', 'flow_stddev', 'flow_min', 'flow_max', '(flow_max - flow_min) / flow_count']
    bitpos_stats_arr_names = ['bitpos_avg', 'bitpos_stddev', 'bitpos_min', 'bitpos_max', '(bitpos_max - bitpos_min) / bitpos_count']
    indep_var_col_names = rpm_stats_arr_names + rop_stats_arr_names + wob_stats_arr_names + flow_stats_arr_names + bitpos_stats_arr_names
    sql = """
        select *
        from
        (
            select
                unnest(features) as feature_arr_indx,
                --Hard-coding this until we can pull this from the prediction table itself
                unnest(ARRAY{feature_names}) as feature,
                unnest(coef_all) as coef
            from
                {input_schema}.{input_table}
        )q
        --Select non-zero coefficients only
        where coef != 0
        order by abs(coef) desc;
    """.format(
        input_schema=input_schema,
        input_table=input_table,
        feature_names=indep_var_col_names
    )
    return sql
