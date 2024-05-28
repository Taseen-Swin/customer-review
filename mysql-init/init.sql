-- Grant all privileges to 'admin' user from any host within the network
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'%' IDENTIFIED BY 'admin';
FLUSH PRIVILEGES;

USE product_reviews;

CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_review TEXT,
    product_class VARCHAR(255),
    product_department VARCHAR(255),
    user_age INT,
    tag VARCHAR(50)
);
