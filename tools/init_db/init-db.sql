CREATE TABLE IF NOT EXISTS users (
    id int AUTO_INCREMENT PRIMARY KEY,
    nickname varchar(20) not null unique,
    email varchar(35) unique,
    coded_password TEXT,
    role enum("OWNER", "LIBRARIAN", "READER")
);
create table if not exists librarians (
	id int auto_increment primary key,
    user_id int references users.id on delete cascade,
    is_hired bool default false,
    director_id int references user.id on delete set null,
    library_id int references libraries.id on delete set null
    -- делать is_hired=false при удалении директора/библиотеки
);
create table if not exists directors (
	id int auto_increment primary key,
    user_id int references users.id on delete cascade,
    library_id int references libraries.id on delete set null
);
CREATE TABLE IF NOT EXISTS libraries (
    id int AUTO_INCREMENT PRIMARY KEY,
    name varchar(20) unique,
    director_id int references user.id on delete cascade,
    description text
);
CREATE TABLE IF NOT EXISTS notifications (
	id int AUTO_INCREMENT primary key,
    author_id int references user.id on delete cascade,
    recipient_id int references user.id on delete cascade,
    title varchar(15),
    content TEXT,
    type varchar(10),
    is_read bool default false
);
create table if not exists books (
	id int AUTO_INCREMENT primary key,
    library_id int not null references libraries.id on delete cascade,
    is_on_hand bool default false,
    inventory_num varchar(15) not null,
	title_ru TEXT,
	title_original TEXT,
	series TEXT,
	lang_of_book varchar(15),
	lang_original varchar(15),
	author_ru varchar(20),
	author_in_original_lang varchar(20),
	writing_year int,
	transfer_year int check (transfer_year > 1000),
	translators TEXT,
	explanation_ru TEXT,
	applications TEXT,
	dimensions varchar(15),
	publication_year int,
	edition_num int,
	publishing_house varchar(15),
	isbn1 integer check (isbn1 REGEXP '^(?:\d{9}[\dX]|\d{13})$' OR isbn1 IS NULL),
	isbn2 integer check (isbn2 REGEXP '^(?:\d{9}[\dX]|\d{13})$' OR isbn2 IS NULL),
	abstract TEXT,
	document_type_id int references document_types.id on delete set null,
	book_genre_id int references book_genres.id on delete set null,
	cover_photo_uuid varchar(40),
	age_of_reader varchar(15),
	quantity int check (quantity >= 0),
	location_id int references locations.id on delete set null,
	condition_id int references book_conditions.id on delete set null,
    pages_quantity int check (pages_quantity > 0),
	UNIQUE(library_id, inventory_num)
);
create table if not exists On_Hands_Books (
	id int AUTO_INCREMENT primary key,
	book_id int references books.id on delete cascade,
	recipient_name varchar(20),
    recipient_id int references users.id,
	issue_date date,
	return_date date,
    check (issue_date <= return_date)
);
create table if not exists book_conditions (
	ID int AUTO_INCREMENT primary key,
	Library_ID int references libraries.id on delete cascade,
	condition_name varchar(15) unique,
    unique(library_id, condition_name)
);
create table if not exists Notification_Settings (
	ID int auto_increment primary key,
	Library_id int references libraries.id on delete cascade,
	Notify_before_days int,
	Notify_after_days int,
	Is_every_day bool
);
create table if not exists Places (
	ID int auto_increment primary key,
	Library_id int references libraries.id on delete cascade,
	Place_name varchar(15) not null,
	Description text,
    unique(library_id, place_name)
);
create table if not exists Shelves (
	ID int auto_increment primary key,
	shelve_name varchar(15) not null,
	Description text,
	Place_id int references Places.id on delete cascade,
    unique(Place_id, shelve_name)
);
create table if not exists Keywords (
	ID int auto_increment primary key,
	Keyword text not null,
	Book_id int references books.id on delete cascade,
	Pages text
);
create table if not exists Topics (
	ID int auto_increment primary key,
	Topic_name varchar(15) not null,
	description text
);
create table if not exists Books_Topics (
	ID int auto_increment primary key,
	Book_id int references books.id on delete cascade,
	Topic_id int references topics.id on delete cascade,
	Pages text
);
create table if not exists Bible_Books (
	ID int auto_increment primary key,
	Ru varchar(30),
	en varchar(30)
);
create table if not exists Bible_Places (
	ID int auto_increment primary key,
	Bible_book_id int references Bible_Books.id on delete cascade,
	Chapter int,
	Verse int, /* стих */
	pages text
);
create table if not exists Book_Genres (
	ID int auto_increment primary key,
	genre_name varchar(15) unique,
	Description text
);
create table if not exists Document_Types (
	ID int auto_increment primary key,
	type_name varchar(15) unique,
	Description text
)