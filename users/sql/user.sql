CREATE VIEW report_users AS
 SELECT username, COUNT(mo.id) as opinion_count, date_joined
 FROM main_opinion mo
  RIGHT JOIN (SELECT * FROM auth_user WHERE id > 1740 OR id <= 2) as au ON au.id=mo.user_id
 GROUP BY au.username, au.date_joined
 ORDER BY date_joined DESC;

CREATE VIEW report_users_who_rated_by_day AS
 SELECT day, COUNT(1) as user_count, avg(count) AS opinion_count_avg, stddev(count) AS opinion_count_stddev
 FROM (
  SELECT COUNT(1) as count, date_trunc('day', date_joined) AS day
  FROM main_opinion mo
   JOIN (SELECT * FROM auth_user WHERE id > 1740 OR id <= 2) as au ON au.id=mo.user_id
  GROUP BY day, user_id
 ) as counts
 GROUP BY day
 ORDER BY day DESC;

CREATE VIEW report_users_by_day AS
 SELECT day, COUNT(1) as user_count, avg(count) AS opinion_count_avg, stddev(count) AS opinion_count_stddev
 FROM (
  SELECT COUNT(mo.id) as count, date_trunc('day', date_joined) AS day
  FROM main_opinion mo
   RIGHT JOIN (SELECT * FROM auth_user WHERE id > 1740 OR id <= 2) as au ON au.id=mo.user_id
  GROUP BY day, user_id
 ) as counts
 GROUP BY day
 ORDER BY day DESC;

