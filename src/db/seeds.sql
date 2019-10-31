drop table characters;
drop table status;
drop table near_tpks;
drop table sessions;

create table status(
    id integer primary key,
    status varchar(8) unique
);

create table characters (
    id integer primary key,
    name varchar(255) not null unique,
    level int2 not null,
    class varchar(8) not null,
    race varchar(8) not null,
    owner int8,
    status references status(status),
    notes text
);

create table sessions (
    id integer primary key,
    date text unique,
    notes text
);

create table near_tpks (
    id integer primary key,
    session_id references sessions(id),
    notes text
);

insert into status (status) values ("alive");
insert into status (status) values ("retired");
insert into status (status) values ("dead");


insert into characters (name, level, class, race, owner, status, notes) values ("Rularuu", 2, "Wizard", "Human", 168009927015661568, 1, "");
insert into characters (name, level, class, race, owner, status, notes) values ("Annari", 2, "Barbarian", "Human", 247328517207883776, 1, "");
insert into characters (name, level, class, race, owner, status, notes) values ("Aineias", 2, "Chirurgeon", "Human", 185039984124755968, 1, "");
insert into characters (name, level, class, race, owner, status, notes) values ("Nora", 2, "Fighter", "Human", 211210914429534209, 1, "");

insert into sessions (date, notes) values ("2019-10-17", "Session 1, character introduction. Fighting Gnoles and exploring.");
insert into near_tpks (session_id, notes) values (1, "Fighting Gnoles, Madcat screwed his HP and died in two hits.");

UPDATE sessions set (notes) = ("Arrival at Northedge, introduction to characters, investigation into deaths of Guardians of Synia. Chased off Gnoles from Aldinox's characters farm.") where id=1;