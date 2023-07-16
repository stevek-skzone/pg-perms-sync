drop table credential;

create table credential (
	name varchar(100),
	cluster_name varchar(100),
	db_name varchar(100),
	credential_type varchar(100),
	create_date timestamptz,
	last_modify_date timestamptz,
	members jsonb				
			
);

NOTIFY pgrst, 'reload schema';

INSERT INTO credential (name, cluster_name, db_name, credential_type, create_date)
VALUES 
('test_group1','pg1','db1','ldap_group',now()),
('test_group2','pg2','db2','ldap_group',now());
