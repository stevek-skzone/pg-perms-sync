drop table credential;

create table credential (
    name varchar(100),
    cluster_name varchar(100),
    db_name varchar(100),
    credential_type varchar(100),
    create_date timestamptz default now(),
    last_modified_date timestamptz,
    members jsonb,
    data jsonb
);

NOTIFY pgrst, 'reload schema';

INSERT INTO credential (name, cluster_name, db_name, credential_type, data)
VALUES 
('test_group1','pg1','db1','ldap_group_sync','{"roles": "read,write"}'),
('test_group2','pg2','db2','ldap_group_sync','{"roles": "read,write"}');
 
--create role read nologin;
--create role write nologin;

select * from credential;


CREATE TABLE job (
    cluster_name varchar(100) NOT NULL,
    db_name  varchar(100) NOT NULL,
    job_type  varchar(100) NOT NULL,
    current_status smallint NOT NULL DEFAULT 0,
    last_run_date TIMESTAMPTZ null,
    PRIMARY KEY(cluster_name, db_name, job_type)
);

CREATE TABLE job_history (
    id bigserial PRIMARY KEY,
    cluster_name varchar(100) NOT NULL,
    db_name  varchar(100) NOT NULL,
    job_type  varchar(100) NOT NULL,
    started TIMESTAMPTZ DEFAULT NOW(),
    status varchar(100),
    data jsonb
);


UPDATE job
SET current_status=1, last_run_date=now()
WHERE job_id IN (
        SELECT job_id FROM job j
        WHERE current_status = 0 AND job_type = 'param' AND
            (last_run_date > now() - interval '15 minutes' or last_run_date is null)
        ORDER BY last_run_date 
        FOR UPDATE SKIP LOCKED LIMIT 1
        )
RETURNING *;

DROP FUNCTION get_job_to_run;
CREATE OR REPLACE FUNCTION get_job_to_run(job_type_name TEXT)
RETURNS TABLE (job_id int, cluster_name varchar(100), db_name varchar(100)) 
AS $$
BEGIN
	RETURN QUERY
    UPDATE job
    SET current_status=1, last_run_date=now()
    WHERE job.job_id IN (
        SELECT j.job_id FROM job j
        WHERE j.current_status = 0 AND j.job_type = job_type_name AND
            (j.last_run_date > now() - interval '15 minutes' or j.last_run_date is null)
        ORDER BY j.last_run_date 
        FOR UPDATE SKIP LOCKED LIMIT 1
    )
    RETURNING job.job_id, job.cluster_name, job.db_name;

END;
$$ LANGUAGE plpgsql;

select * from get_job_to_run('ldap_group')

INSERT INTO job_history (cluster_name, db_name, job_type, status, data)