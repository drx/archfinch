CREATE OR REPLACE FUNCTION wilson_score(item_id integer) RETURNS real
    AS $$
    DECLARE 
        z CONSTANT real := 2;
        extremity_factor CONSTANT integer := 3;
        positive integer := 0;
        negative integer := 0;
        total integer := 0;
        phat real;
        rating_row record;
    BEGIN
    FOR rating_row in SELECT rating, count(1) as count from main_opinion where item_id=$1 group by rating
    LOOP
        CASE rating_row.rating
            WHEN 5 THEN positive := positive + rating_row.count*extremity_factor;
            WHEN 4 THEN positive := positive + rating_row.count;
            WHEN 2 THEN negative := negative + rating_row.count;
            WHEN 1 THEN negative := negative + rating_row.count*extremity_factor;
            ELSE NULL;
        END CASE;
    END LOOP;
    total := positive + negative;
    if total = 0 then return 0; end if;

    phat := positive::real/total::real;
    return (phat + z*z/(2*total) - z*sqrt((phat*(1-phat)+z*z/(4*total))/total))/(1+z*z/total);
    END;
    $$ LANGUAGE plpgsql;
