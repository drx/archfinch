CREATE OR REPLACE FUNCTION update_item_rated(a_user integer, item integer) RETURNS VOID AS
$$
DECLARE
    user_cursor CURSOR FOR SELECT m2.user_id AS user_id, sum(2-abs(m1.rating- m2.rating)) AS value
            FROM main_opinion m1
            INNER JOIN main_opinion m2
             ON (m1.item_id = m2.item_id AND m1.user_id=a_user)
            INNER JOIN main_opinion m3
             ON (m2.user_id = m3.user_id AND m3.item_id = item)
            GROUP BY m2.user_id;
BEGIN
    FOR u IN user_cursor
    LOOP
        -- UPDATE or INSERT as necessary
        <<update_or_insert>> LOOP
            UPDATE main_similarity SET value = u.value WHERE user1_id = a_user AND user2_id = u.user_id;
            IF found THEN EXIT update_or_insert; END IF;
            BEGIN INSERT INTO main_similarity(user1_id, user2_id, value) VALUES (a_user, u.user_id, u.value); EXIT update_or_insert;
                  EXCEPTION WHEN unique_violation THEN END;
        END LOOP;
        <<update_or_insert>> LOOP
            UPDATE main_similarity SET value = u.value WHERE user2_id = a_user AND user1_id = u.user_id;
            IF found THEN EXIT update_or_insert; END IF;
            BEGIN INSERT INTO main_similarity(user2_id, user1_id, value) VALUES (a_user, u.user_id, u.value); EXIT update_or_insert;
                  EXCEPTION WHEN unique_violation THEN END;
        END LOOP;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

