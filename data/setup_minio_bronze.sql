-- Enable S3 access and JSON reading
INSTALL s3;
LOAD s3;

SET s3_region='us-east-1';
SET s3_endpoint='192.168.16.3:9000';
SET s3_access_key_id='minioadmin';
SET s3_secret_access_key='minioadmin123';
SET s3_use_ssl=FALSE;
SET s3_url_style='path';

-- reads all json from bucket bronze

CREATE OR REPLACE VIEW bronze_layer_data AS
SELECT * FROM read_json_auto('s3://bronze/*.json');


