
"""
Collection of SQL snippets used in model-building.
June-2015: Srivatsan Ramanujam <sramanujam@pivotal.io> : Ported SQL snippets originally authored by Rashmi Raghu <rraghu@pivotal.io>
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
                array[depth_avg, depth_stddev, depth_min, depth_max, (depth_max - depth_min) / depth_count] as depth_stats_arr,
                array[rpm_avg, rpm_stddev, rpm_min, rpm_max, (rpm_max - rpm_min) /rpm_count] as rpm_stats_arr,
                array[rop_avg, rop_stddev, rop_min, rop_max, (rop_max - rop_min) / rop_count] as rop_stats_arr,
                array[wob_avg, wob_stddev, wob_min, wob_max, (wob_max - wob_min) / wob_count] as wob_stats_arr,
                array[flow_avg, flow_stddev, flow_min, flow_max, (flow_max - flow_min) / flow_count] as flow_stats_arr,
                array[bitpos_avg, bitpos_stddev, bitpos_min, bitpos_max, (bitpos_max - bitpos_min) / bitpos_count] as bitpos_stats_arr
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
                end::integer as failure_flag_1hr_ahead,
                case when random() <= 0.7 then 1 
                     else 0 
                end::integer as include_in_training,
                *
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
        A sql code block    
    """    
    sql = """   
    """.format(
        input_schema=input_schema,
        input_table=input_table,
        output_schema=output_schema,
        output_table=output_table        
    )
    return sql


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
    

def predict_model(input_schema, input_table, output_schema, output_table):
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
    """
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