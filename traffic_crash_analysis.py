import streamlit as st
import pandas as pd
import mysql.connector
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="TRAFFIC_ANALYSIS"
)

cursor = connection.cursor()

st.sidebar.title("TRAFFIC CRASH ANALYSIS")

page = st.sidebar.radio(
    "Go to",
    ["DESCRIPTION", "EXPLORATION OF ANALYSIS", "CONCLUSION"]
)
if page == "DESCRIPTION":
    st.title("Description")
    st.write("The goal of this research is to analyze a large-scale traffic crash dataset to identify trends in injury severity, contributory causes, and accident patterns. After the dataset was successfully loaded into SQL and transformed into a structured format, structured queries were run to examine and evaluate the data.")
 
elif page == "EXPLORATION OF ANALYSIS":
    st.title("Exploration of Analysis")
    st.write("Select a query below to explore crash results:")

    query_option = st.selectbox(
        "CHOOSE ANALYSIS",
        [
            "The top 5 most hazardous weather and crash type combinations for all crashers",
            "The top ten streets with the most injuries from crashes",
            "The proportion of each crash type that resulted in injuries.",
            "The monthly peak crash hour",
            "The top 5 primary causes of crashes during night time (CRASH_HOUR ≥ 18).",
            "The average number of injuries during the day and at night",
            "Which traffic control device type has the highest average injuries per crash.",
            "Determine which five places (latitude/longitude) have the highest crash frequency.",
            "The top 5 streets with the highest injury rate, considering only streets with more than 100 crashes.",
            "Determine the most prevalent crash type for each year.",
            "Day of the week has the highest hourly average of crashes.",
            "Determine high-risk periods: Sort the hours into buckets (morning, afternoon, evening, and night).Determine which bucket has the most crashes with injuries.",
            "For each type of crash, identify the top three contributing factors;(using window functions such as RANK() or ROW_NUMBER().)",
            "The crash growth rate from year to year.(using of the window function LAG()) HCL",
            "Determine hotspot areas:Group nearby locations (round latitude & longitude to 2 decimal places) Find top 10 zones with highest crashes"
        ]
    )

    if query_option == "The top 5 most hazardous weather and crash type combinations for all crashers":
        st.subheader("The top 5 most hazardous weather and crash type combinations for all crashers")
        query= """
        select
        WEATHER_CONDITION,
        FIRST_CRASH_TYPE,
        count(*) as total_crashers
        from traffic_data
        group by WEATHER_CONDITION, FIRST_CRASH_TYPE
        order by total_crashers desc
        limit 5;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)
        
        st.info("""
                Observation: 
                Conditions are not the primary cause of most crashes, which happen in clear weather, the majority of collisions are parked motor, rear-end and sideswipe, indicating traffic jams and close driving,
                the general trend indicates that traffic density and human error are more important than weather.
                """)
        
    elif query_option == "The top ten streets with the most injuries from crashes":
        st.subheader("The top ten streets with the most injuries from crashes")
        query = """
        select
        STREET_NAME,
        count(*) as injury_crashers
        from traffic_data
        where INJURIES_TOTAL > 0
        group by STREET_NAME
        order by injury_crashers desc
        limit 10;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation:
                Major arterial routes like Western Avenue, Pulaski Road, and Ashland Avenue have a high concentration of injury crashes, indicating high-risk, high-traffic areas Additionally, streets like Cicero, Halsted, and Kedzie routinely have high injury rates,
                indicating ongoing safety concerns along several important thoroughfares  Overall, 
                the pattern indicates that busy business and commuter roads are the main locations where injuries occur, 
                perhaps as a result of the speed–volume mix and frequent junctions.
                """)


    elif query_option == "The proportion of each crash type that resulted in injuries.":
        st.subheader("The proportion of each crash type that resulted in injuries.")
        query="""
        select
        FIRST_CRASH_TYPE,
        count(*) as total_crashers,
        sum(case when INJURIES_TOTAL > 0 then 1 else 0 end) as injury_crashers,
        round(sum(case when INJURIES_TOTAL > 0 then 1 else 0 end) *100.0 / count(*),2
        ) as injury_percentage
        from traffic_data
        group by FIRST_CRASH_TYPE
        order by injury_percentage desc;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation:Among all collision types, pedestrians and cyclists have the highest risk of injury.
                Although the majority of vehicle-to-vehicle collisions occur often, the chance of injuries is generally lower.
                """)
    
    elif query_option == "The monthly peak crash hour":
        st.subheader("The monthly peak crash hour")
        query= """
        select 
        CRASH_MONTH,CRASH_HOUR,total_crashers
        from (select CRASH_MONTH,
        CRASH_HOUR,
        count(*) as total_crashers,
        row_number() over (
        partition by CRASH_MONTH
        order by count(*) desc) as rn
        from traffic_data
        group by CRASH_MONTH, CRASH_HOUR
        )t
        where rn=1
        order by CRASH_MONTH;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Peak crashes consistently occur during afternoon rush hours (3–4 PM, and 5 PM in late year months).
                This indicates crashes are strongly tied to commuter traffic congestion rather than specific months.
                The pattern suggests human activity timing (work/return travel) is the dominant factor in crash frequency.
                """)
        
    elif query_option == "The top 5 primary causes of crashes during night time (CRASH_HOUR ≥ 18).":
        st.subheader("The top 5 primary causes of crashes during night time (CRASH_HOUR ≥ 18).")
        query = """
        select
        PRIM_CONTRIBUTORY_CAUSE,
        count(*) as total_crashers
        from traffic_data
        where CRASH_HOUR >= 18
        group by PRIM_CONTRIBUTORY_CAUSE
        order by total_crashers desc
        limit 5;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Evening crashes are mostly driven by driver behaviour issues like not yielding and following too closely,
                not external conditions.A large share is “unable to determine,
                suggesting complexity or missing data in crash reporting.
                """)
        
    elif query_option == "The average number of injuries during the day and at night":
        st.subheader("The average number of injuries during the day and at night")
        query= """
        select 
        case when LIGHTING_CONDITION like 'DAYLIGHT%' then 'DAYLIGHT'
        else 'DARKNESS'
        end as Light_category,
        round(avg(INJURIES_TOTAL), 2) as avg_injuries
        from traffic_data
        where LIGHTING_CONDITION like 'DAYLIGHT%' or LIGHTING_CONDITION like 'DARKNESS%'
        group by light_category;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Crashes occurring in darkness result in more injuries on average (0.27) than those in daylight (0.21)
                """)
        
    elif query_option == "Which traffic control device type has the highest average injuries per crash.":
        st.subheader("Which traffic control device type has the highest average injuries per crash.")
        query= """
        select TRAFFIC_CONTROL_DEVICE,
        round(avg(INJURIES_TOTAL), 2) as avg_injuries
        from traffic_data
        group by TRAFFIC_CONTROL_DEVICE
        order by avg_injuries desc
        limit 1;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Locations with bicycle crossing signs have the greatest average number of injuries per crash (0.66),
                suggesting that there is a higher danger in places where bikes and cars meet.
                """)
    elif query_option == "Determine which five places (latitude/longitude) have the highest crash frequency.":
        st.subheader("Determine which five places (latitude/longitude) have the highest crash frequency.")
        query= """
        select LATITUDE,
        LONGITUDE,
        count(*) as crash_count
        from traffic_data
        where LATITUDE is not null
        and LONGITUDE is not null
        group by LATITUDE, LONGITUDE
        order by crash_count desc
        limit 5;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: A disproportionately high number of crashes occur in a small number of specific geographic regions;
                the top hotspot recorded 1,247 crashes.
                Certain high-risk crossroads or road segments may significantly contribute to the overall volume of crashes,
                as shown by the steep decline in numbers from the first site to subsequent ones.
                """)
        
    elif query_option == "The top 5 streets with the highest injury rate, considering only streets with more than 100 crashes.":
        st.subheader("The top 5 streets with the highest injury rate, considering only streets with more than 100 crashes.")
        query= """
        select 
        STREET_NAME,
        count(*) as crash_count,
        round(sum(INJURIES_TOTAL)/
        count(*), 2) as injury_rate
        from traffic_data
        group by STREET_NAME
        having count(*) >100
        order by injury_rate desc
        limit 5;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Marquette Dr and Fifth Ave have the highest injury rates per crash,
                indicating crashes on these roads tend to be more severe.
                Douglas Blvd has an injury rate of 0.39 injuries per crash across 390 crashes,
                South Chicago Ave stands out because it combines a high injury rate with a large number of crashes,
                making it a critical safety concern.
                """)
        
    elif query_option == "Determine the most prevalent crash type for each year.":
        st.subheader("Determine the most prevalent crash type for each year.")
        query= """
        select
        year,
        CRASH_TYPE,
        crash_freq
        from(select
        year,
        CRASH_TYPE,
        count(*) as crash_freq,
        row_number() over(
        partition by year
        order by count(*) desc) as rn
        from traffic_data
        group by year, CRASH_TYPE
        )t
        where rn= 1
        order by year;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Across all years, “No Injury / Drive Away” is consistently the most common crash type,
                showing that most incidents are minor.
                The frequency of such crashes increases steadily from 2020 to 2024,
                indicating rising crash volume over time.
                """)
        
    elif query_option == "Day of the week has the highest hourly average of crashes.":
        st.subheader("Day of the week has the highest hourly average of crashes.")
        query= """
        select 
        t1.CRASH_DAY_OF_WEEK,
        round(avg(t2.crash_count), 2) as avgcrash_perhour
        from traffic_data t1 join(select
        CRASH_DAY_OF_WEEK,
        CRASH_HOUR,
        count(*) as crash_count
        from traffic_data
        group by CRASH_DAY_OF_WEEK, CRASH_HOUR
        )t2 
        on t1.CRASH_DAY_OF_WEEK = t2.CRASH_DAY_OF_WEEK
        group by  t1.CRASH_DAY_OF_WEEK
        order by avgcrash_perhour desc limit 1;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Day 6 (Saturday) is the most crash-prone day,
                with the highest average crash volume per hour (~4455 crashes/hour level activity pattern).
                """)
        
    elif query_option == "Determine high-risk periods: Sort the hours into buckets (morning, afternoon, evening, and night).Determine which bucket has the most crashes with injuries.":
        st.subheader("Determine high-risk periods: Sort the hours into buckets (morning, afternoon, evening, and night).Determine which bucket has the most crashes with injuries.")
        query= """
        select
        case 
        when CRASH_HOUR between 5 and 11 then 'Morning'
        when CRASH_HOUR between 12 and 16 then 'Afternoon'
        when CRASH_HOUR between 17 and 20 then 'Evening'
        else 'Night'
        end as buckets,
        sum(INJURIES_TOTAL) as total_injuries
        from traffic_data
        group by buckets
        order by total_injuries desc;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Afternoon hours have the highest total injuries,
                Morning and evening follow closely and Night has slightly lower total injuries.
                """)

    elif query_option == "For each type of crash, identify the top three contributing factors;(using window functions such as RANK() or ROW_NUMBER().)":
        st.subheader("For each type of crash, identify the top three contributing factors;(using window functions such as RANK() or ROW_NUMBER().)")
        query="""
        select 
        FIRST_CRASH_TYPE,
        PRIM_CONTRIBUTORY_CAUSE,
        total_crashes
        from(select
        FIRST_CRASH_TYPE,PRIM_CONTRIBUTORY_CAUSE,
        count(*) as total_crashes,
        row_number() over (partition by FIRST_CRASH_TYPE
        order by count(*) desc
        ) as rn 
        from traffic_data
        group by FIRST_CRASH_TYPE,PRIM_CONTRIBUTORY_CAUSE
        )t where rn <= 3
        order by FIRST_CRASH_TYPE, total_crashes desc;
        """  
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Unable to Determine" is the most common contributing factor in the majority of crash types.
                Clear behavioral factors, such as failing to yield, following too closely, and improperly overtaking, constantly dominate crash types, particularly angle, rear-end, and turning crashes.
                Some crash types are highly associated with particular behaviors, such as turning → inappropriate signaling or failure to yield, head-on → driving on the wrong side, and rear-end → following too closely.
                """)

    elif query_option == "The crash growth rate from year to year.(using of the window function LAG()) HCL":
        st.subheader("The crash growth rate from year to year.(using of the window function LAG()) HCL")
        query="""
        with every_year_crashes as (
        select
        year,
        count(*) as total_crashes
        from traffic_data
        group by year
        )
        select 
        year,
        total_crashes,
        lag(total_crashes) over (order by year) as previous_year_crashes,
        round((total_crashes - lag(total_crashes) over (order by year)) *100.0/lag(total_crashes) over (order by year),2
        ) as year_growth_percentage
        from every_year_crashes;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: Crash totals rise from 2020 and peak in 2024 (110,853), then slightly decline in 2025.
                """)
        
    elif query_option == "Determine hotspot areas:Group nearby locations (round latitude & longitude to 2 decimal places) Find top 10 zones with highest crashes":
        st.subheader("Determine hotspot areas:Group nearby locations (round latitude & longitude to 2 decimal places) Find top 10 zones with highest crashes")
        query= """
        select 
        round(LATITUDE) as latitude_zone,
        round(LONGITUDE) as longitude_zone,
        count(*) as total_crashes
        from traffic_data
        where LATITUDE is not null and LONGITUDE is not null
        group by latitude_zone, longitude_zone
        order by total_crashes desc
        limit 10;
        """
        df= pd.read_sql(query, connection)
        st.dataframe(df)

        st.info("""
                Observation: The majority of crashes are around the ~(42, -88) zone, showing a highly dense crash hotspot region.
                A small number of records at (0,0) represent invalid or missing geolocation data.
                """)
        
elif page == "CONCLUSION":
        st.title("Conclusion")

        st.write("""
        Traffic crashes are driven far more by *human behavior and location patterns*
        than by external factors like weather conditions.
        This indicates that road safety improvements should focus more on driver behavior,
        traffic control, and high-risk locations rather than only environmental conditions.
        """)
        st.subheader("Learnings")

        st.markdown("""
        -summarized crash patterns, used GROUP BY with aggregate functions (COUNT, SUM, AVG).
        -Time-based and conditional categories created using CASE WHEN.
        -WHERE and HAVING clauses were used to filter important data.
        -For ranking and trend analysis, window functions (ROW_NUMBER, LAG) were utilized.
        -Complex queries were organized step-by-step using CTEs and subqueries.
        -Derived parameters such as growth rate, percentages, and injury rate were calculated.
        -To find crash sites, spatial grouping using latitude and longitude was carried out.
        """)
        st.info("End of Analysis-Thank you")
        
        