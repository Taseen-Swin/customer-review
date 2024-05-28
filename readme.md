docker-compose build
docker-compose up
docker-compose exec db mysql -u root -p

USE product_reviews;

CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_review TEXT,
    product_class VARCHAR(255),
    product_department VARCHAR(255),
    user_age INT,
    tag VARCHAR(50)
);
