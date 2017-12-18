DROP TABLE IF EXISTS `Students`;
DROP TABLE IF EXISTS `Quiz`;
DROP TABLE IF EXISTS `Results`;

DROP TABLE IF EXISTS `Blog`;
DROP TABLE IF EXISTS `Comment`;
DROP TABLE IF EXISTS `Account`;

CREATE TABLE `Blog`(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    blog_body BLOB,
    author TEXT,
    entry_date DATE,
    mod_date Date,
    blog_title TEXT,
    blog_tags Text,
    blog_picture LONGBLOB,
    visibility bollean not null default 0
    );

CREATE TABLE `Comment`(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    c_body TEXT,
    c_by TEXT,
    c_entry_date DATE,
    c_mod_date Date,
    blog_id INT,
    FOREIGN KEY(blog_id) REFERENCES Blog(id)
    );

CREATE TABLE `Students`(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fname TEXT,
    lname TEXT
    );

CREATE TABLE `Quiz`(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    questions INT,
    quiz_date DATE
    );

CREATE TABLE `Account`(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username INT,
    password Text,
    email Text
    );



