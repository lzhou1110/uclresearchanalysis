/* 20180715 */
/* https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/user-object.html */
CREATE TABLE IF NOT EXISTS `user` (
    /* Basic info */
    `id` bigint unsigned NOT NULL,
    `name` varchar(140) NOT NULL,
    `screen_name` varchar(30) NOT NULL,  
    `location` varchar(180) default NULL,
    `url` varchar(400) default NULL,
    `description` varchar(300) default NULL,
    `protected` tinyint default '0',
    `verified` tinyint default '0',
    /* Counts */
    `followers_count` int unsigned default '0',
    `friends_count` int unsigned default '0',
    `listed_count` int unsigned default '0',
    `favourites_count` int unsigned default '0',
    `statuses_count` int unsigned default '0',
    /* Other attributes */
    `created_at` timestamp NOT NULL default '0000-00-00 00:00:00',
    `geo_enabled` tinyint default '0',
    `lang` char(2) default NULL,
    `contributors_enabled` tinyint default '0',
    PRIMARY KEY  (`id`),
    UNIQUE KEY `screen_name` (`screen_name`)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;