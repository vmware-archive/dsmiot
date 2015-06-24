
"""
Collection of SQL snippets used in model-building.
May-2015: Rashmi Raghu <rraghu@pivotal.io> - SQL snippets for feature generation, model building & scoring
June-2015: Srivatsan Ramanujam <sramanujam@pivotal.io> - Ported SQL snippets into python functions + added snippets to populate heatmap & time series plots
"""

def create_features(input_schema, input_table, output_schema, output_table):
    """
        Inputs:
        =======
        input_schema (str): The schema containing the input table
        input_table (str): The table in the input_schema containing data from the wells
        output_schema (str) : The schema for storing results of current prediction experiments
        output_table (str) : The table containig the engineered features, ready for training a model
        Outputs:
        ========
        A sql code block
    """
    sql = """
        drop table if exists {output_schema}.{output_table};
        create table {output_schema}.{output_table} 
        as 
        (
            select 
                well_id,
                run_id,
                window_id,
                row_id,
                global_window_id,
                failure_flag_for_full_run,
                ts_utc,
                depth,
                rpm,
                rop,
                wob,
                flow_in_rate,
                bit_position,
                array[depth_count, rpm_count, rop_count, wob_count, flow_count, bitpos_count] as count_arr,
                array['depth_count', 'rpm_count', 'rop_count', 'wob_count', 'flow_count', 'bitpos_count'] as count_arr_names,
                array[depth_avg, depth_stddev, depth_min, depth_max, (depth_max - depth_min) / depth_count] as depth_stats_arr,
                array['depth_avg', 'depth_stddev', 'depth_min', 'depth_max', '(depth_max - depth_min) / depth_count'] as depth_stats_arr_names,
                array[rpm_avg, rpm_stddev, rpm_min, rpm_max, (rpm_max - rpm_min) /rpm_count] as rpm_stats_arr,
                array['rpm_avg', 'rpm_stddev', 'rpm_min', 'rpm_max', '(rpm_max - rpm_min) /rpm_count'] as rpm_stats_arr_names,
                array[rop_avg, rop_stddev, rop_min, rop_max, (rop_max - rop_min) / rop_count] as rop_stats_arr,
                array['rop_avg', 'rop_stddev', 'rop_min', 'rop_max', '(rop_max - rop_min) / rop_count'] as rop_stats_arr_names,
                array[wob_avg, wob_stddev, wob_min, wob_max, (wob_max - wob_min) / wob_count] as wob_stats_arr,
                array['wob_avg', 'wob_stddev', 'wob_min', 'wob_max', '(wob_max - wob_min) / wob_count'] as wob_stats_arr_names,
                array[flow_avg, flow_stddev, flow_min, flow_max, (flow_max - flow_min) / flow_count] as flow_stats_arr,
                array['flow_avg', 'flow_stddev', 'flow_min', 'flow_max', '(flow_max - flow_min) / flow_count'] as flow_stats_arr_names,
                array[bitpos_avg, bitpos_stddev, bitpos_min, bitpos_max, (bitpos_max - bitpos_min) / bitpos_count] as bitpos_stats_arr,
                array['bitpos_avg', 'bitpos_stddev', 'bitpos_min', 'bitpos_max', '(bitpos_max - bitpos_min) / bitpos_count'] as bitpos_stats_arr_names
            from (
                    select 
                        well_id,
                        run_id,
                        row_number() over (partition by well_id, run_id order by row_id) as window_id,
                        row_id,
                        row_number() over (order by well_id, run_id) as global_window_id,
                        failure_flag as failure_flag_for_full_run,
                        ts_utc,
                        depth,
                        rpm,
                        rop,
                        wob,
                        flow_in_rate,
                        bit_position,
                        --
                        avg(depth) over (w) as depth_avg,
                        stddev_samp(depth) over (w) as depth_stddev,
                        min(depth) over (w) as depth_min,
                        max(depth) over (w) as depth_max,
                        count(depth) over (w) as depth_count,
                        --
                        avg(rpm) over (w) as rpm_avg,
                        stddev_samp(rpm) over (w) as rpm_stddev,
                        min(rpm) over (w) as rpm_min,
                        max(rpm) over (w) as rpm_max,
                        count(rpm) over (w) as rpm_count,
                        --
                        avg(rop) over (w) as rop_avg,
                        stddev_samp(rop) over (w) as rop_stddev,
                        min(rop) over (w) as rop_min,
                        max(rop) over (w) as rop_max,
                        count(rop) over (w) as rop_count,
                        --
                        avg(wob) over (w) as wob_avg,
                        stddev_samp(wob) over (w) as wob_stddev,
                        min(wob) over (w) as wob_min,
                        max(wob) over (w) as wob_max,
                        count(wob) over (w) as wob_count,
                        --
                        avg(flow_in_rate) over (w) as flow_avg,
                        stddev_samp(flow_in_rate) over (w) as flow_stddev,
                        min(flow_in_rate) over (w) as flow_min,
                        max(flow_in_rate) over (w) as flow_max,
                        count(flow_in_rate) over (w) as flow_count,
                        --
                        avg(bit_position) over (w) as bitpos_avg,
                        stddev_samp(bit_position) over (w) as bitpos_stddev,
                        min(bit_position) over (w) as bitpos_min,
                        max(bit_position) over (w) as bitpos_max,
                        count(bit_position) over (w) as bitpos_count
                    from 
                        {input_schema}.{input_table}
                    window w as (partition by well_id, run_id order by ts_utc range between '1 hour'::interval preceding and current row)
            ) t
        ) distributed by (global_window_id);    
    """.format(
        input_schema=input_schema,
        input_table=input_table,
        output_schema=output_schema,
        output_table=output_table
    )
    return sql
    
def add_label_to_features(input_schema, input_table, output_schema, output_table):
    """
        Inputs:
        =======
        input_schema (str): The schema containing the input table
        input_table (str): The table in the input_schema containing data from the wells
        output_schema (str) : The schema for storing results of current prediction experiments
        output_table (str) : The table containig the engineered features, ready for training a model
        Outputs:
        ========
        A sql code block    
    """
    sql = """
        -- Flagging failure ONLY 1 hour ahead NOT for the whole run
        drop table if exists {output_schema}.{output_table};
        create table {output_schema}.{output_table} 
        as 
        (
            select 
                case when failure_flag_for_full_run = 1 and ts_utc >= max_ts_utc_per_run - '1 hour'::interval then 1
                     else 0
                end::integer as flag_dep_var,
                random() as seed,
                *,
                rpm_stats_arr || rop_stats_arr || wob_stats_arr || flow_stats_arr || bitpos_stats_arr as indep_var_col,
                rpm_stats_arr_names || rop_stats_arr_names || wob_stats_arr_names || flow_stats_arr_names || bitpos_stats_arr_names as indep_var_col_names
            from (
                select 
                    *, 
                    max(ts_utc) over (partition by well_id, run_id) as max_ts_utc_per_run
                from {input_schema}.{input_table}
            ) t
        ) distributed by (global_window_id);    
    """.format(
        input_schema=input_schema,
        input_table=input_table,
        output_schema=output_schema,
        output_table=output_table
    )
    return sql

def create_train_and_test_set(input_schema, input_table, output_schema, output_table):
    """
        Inputs:
        =======
        input_schema (str): The schema containing the input table
        input_table (str): The table in the input_schema containing data from the wells
        output_schema (str) : The schema for storing results of current prediction experiments
        output_table (str) : The table containig the engineered features, ready for training a model
        Outputs:
        ========
        sql (str) : A sql code block 
        training_table: the name of the training table
        test_table: the name of the test table   
    """    
    sql = """  
        -- Training table
        drop table if exists {output_schema}.{output_table}_train;
        create table {output_schema}.{output_table}_train
        (
            select 
                *
            from 
                {input_schema}.{input_table}
            where 
                seed <= 0.70
        ) distributed by (global_window_id);
        
        -- Test table
        drop table if exists {output_schema}.{output_table}_test;
        create table {output_schema}.{output_table}_test
        (
            select 
                *
            from 
                {input_schema}.{input_table}
            where 
                seed > 0.70
        ) distributed by (global_window_id);
                
    """.format(
        input_schema=input_schema,
        input_table=input_table,
        output_schema=output_schema,
        output_table=output_table        
    )
    return (sql, output_table+'_train', output_table+'_test')


def train_model(input_schema, input_table, output_schema, output_table):
    """
        Inputs:
        =======
        input_schema (str): The schema containing the input table
        input_table (str): The table in the input_schema containing data from the wells
        output_schema (str) : The schema for storing results of current prediction experiments
        output_table (str) : The table containig the engineered features, ready for training a model
        Outputs:
        ========
        A sql code block       
    """
    sql = """
        drop table if exists {output_schema}.{output_table};
        select madlib.elastic_net_train(
            '{input_schema}.{input_table}',
            '{output_schema}.{output_table}',
            'flag_dep_var',
            'indep_var_col',
            'binomial',
            1.0,
            0.001
        );    
    """.format(
        input_schema=input_schema,
        input_table=input_table,
        output_schema=output_schema,
        output_table=output_table
    )
    return sql
    

def predict_model(mdl_schema, mdl_table, scoring_schema, scoring_table, output_schema, output_table):
    """
        Inputs:
        =======
        mdl_schema (str): The schema containing the model table
        mdl_table (str): The table in the mdl_schema containing model coefficients
        scoring_schema (str): Schema containing data to be scored
        scoring_table (str): Table containing scoring data
        output_schema (str) : The schema for storing results of current prediction experiments
        output_table (str) : The table containig the engineered features, ready for training a model
        Outputs:
        ========
        A sql code block       
    """    
    sql = """
        drop table if exists {output_schema}.{output_table};
        create table {output_schema}.{output_table}
        as
        (
            select 
                   *,
                   madlib.elastic_net_binomial_predict(coef_all, intercept, indep_var_col) as pred,
                   madlib.elastic_net_binomial_prob (coef_all, intercept, indep_var_col) as prob
            from {mdl_schema}.{mdl_table} mdl,
                 {scoring_schema}.{scoring_table} score
        ) distributed randomly;
    """.format(
        mdl_schema=mdl_schema,
        mdl_table=mdl_table,
        scoring_schema=scoring_table,
        scoring_table=scoring_table,
        output_schema=output_schema,
        output_table=output_table        
    )
    return sql
    
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
    
    
    
    
    
    
    
    
    
    
    
    