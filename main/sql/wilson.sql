CREATE OR REPLACE FUNCTION wilson_score(item_id integer) RETURNS integer
    AS $$
    from math import sqrt
    z = 2
    extremity_factor = 3

    ratings_q = plpy.execute("SELECT rating, count(1) as count from main_opinion group by rating having item_id=$1 order by rating asc", [item_id])
    ratings = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for rating in ratings_q:
        ratings[rating['rating']+1] = rating['count']
    positive = ratings[4] + ratings[5]*extremity_factor
    negative = ratings[2] + ratings[1]*extremity_factor
    total = positive+negative
    if total == 0: 
        return 0
        
    observation = float(positive)/total
    
    return (observation + z*z/(2*total) - z*sqrt((observation*(1-observation)+z*z/(4*total))/total))/(1+z*z/total)    
    
    $$ LANGUAGE plpythonu;
