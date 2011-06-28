CREATE OR REPLACE FUNCTION wilson_score(arg_item_id integer, lower_bound boolean) RETURNS real
    AS $$
    DECLARE 
        z CONSTANT real := 2;
        extremity_factor CONSTANT integer := 3;
        positive integer := 0;
        negative integer := 0;
        total integer := 0;
        bound_factor integer := 1;
        phat real;
        rating_row record;
        submitter integer;
    BEGIN
    SELECT COALESCE(submitter_id, 0) INTO submitter FROM main_item WHERE id=arg_item_id;
    FOR rating_row in SELECT rating, count(1) as count from main_opinion where item_id=arg_item_id and user_id != submitter group by rating
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
    if total = 0 and lower_bound then return 0; end if;
    if total = 0 and not lower_bound then return 1; end if;

    if lower_bound then bound_factor = -1; else bound_factor = 1; end if;

    phat := positive::real/total::real;
    return (phat + z*z/(2*total) + bound_factor*z*sqrt((phat*(1-phat)+z*z/(4*total))/total))/(1+z*z/total);
    END;
    $$ LANGUAGE plpgsql;
