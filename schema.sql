-- Minimal schema for BotDiscord
-- Adjust database name/charset as needed

-- CREATE DATABASE IF NOT EXISTS `jipu4543_ChallengeDiscord` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- USE `jipu4543_ChallengeDiscord`;

CREATE TABLE IF NOT EXISTS users (
	id BIGINT PRIMARY KEY,
	username VARCHAR(100) NOT NULL,
	score INT NOT NULL DEFAULT 0,
	last_participation DATETIME NULL,
	created_at DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS challenges (
	id INT AUTO_INCREMENT PRIMARY KEY,
	title VARCHAR(255) NOT NULL,
	question TEXT NOT NULL,
	answer_expected TEXT NOT NULL,
	subject VARCHAR(100) NOT NULL,
	difficulty TINYINT NOT NULL,
	published_at DATE NOT NULL,
	points_value INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS submissions (
	id INT AUTO_INCREMENT PRIMARY KEY,
	user_id BIGINT NOT NULL,
	challenge_id INT NOT NULL,
	response TEXT NOT NULL,
	is_correct BOOLEAN NOT NULL,
	submitted_at DATE NOT NULL,
	CONSTRAINT fk_sub_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
	CONSTRAINT fk_sub_chal FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
