SELECT COUNT(1) AS doc_count FROM ducklake; -- get total document count
SELECT DISTINCT(overall_status) FROM ducklake; -- get all unique status names
SELECT * FROM ducklake LIMIT 5; -- returns all columns of 5 documents
SELECT overall_status FROM ducklake WHERE nct_id LIKE 'NCT000%'; -- return overall_status where nct_id starts with NCT000