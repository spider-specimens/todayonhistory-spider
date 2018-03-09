create database tih;

\c tih;

-- event table
create table events (
    id serial,
    title varchar(200) not null,
    description varchar(200),
    cover varchar(200),
    body text,
    month int not null,
    day int not null,
    target varchar(30) not null,
    target_id varchar(30) not null,
    target_detail_url varchar(200),
    create_time int not null,
    update_time int not null,
    status int not null
);