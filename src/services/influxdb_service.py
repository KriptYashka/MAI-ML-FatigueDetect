from influxdb_client import InfluxDBClient
from influxdb_client.client.query_api import QueryApi
from typing import List, Dict, Optional
import pandas as pd
import os


class InfluxDBService:
    def __init__(
        self,
        url: str = None,
        token: str = None,
        org: str = None,
        bucket: str = None,
    ):
        self.url = url or os.getenv("INFLUXDB_URL", "http://localhost:8086")
        self.token = token or os.getenv("INFLUXDB_TOKEN", "my-token")
        self.org = org or os.getenv("INFLUXDB_ORG", "my-org")
        self.bucket = bucket or os.getenv("INFLUXDB_BUCKET", "my-bucket")
        self._client: Optional[InfluxDBClient] = None
        self._query_api: Optional[QueryApi] = None

    def connect(self) -> None:
        self._client = InfluxDBClient(
            url=self.url,
            token=self.token,
            org=self.org,
        )
        self._query_api = self._client.query_api()
        print(f"Connected to InfluxDB at {self.url}")

    def disconnect(self) -> None:
        if self._client:
            self._client.close()

    def query_data(
        self,
        measurement: str,
        fields: List[str],
        start: str = "-1h",
        stop: str = None,
    ) -> pd.DataFrame:
        if not self._query_api:
            raise ConnectionError("Not connected to InfluxDB. Call connect() first.")

        flux_query = self._build_flux_query(measurement, fields, start, stop)
        result = self._query_api.query_data_frame(flux_query)
        
        if result.empty:
            return pd.DataFrame()
        
        return result

    def _build_flux_query(
        self,
        measurement: str,
        fields: List[str],
        start: str = "-1h",
        stop: str = None,
    ) -> str:
        fields_filter = ' or r["_field"] == '.join([f'"{f}"' for f in fields])
        
        stop_clause = f', stop: {stop}' if stop else ''
        
        query = f'''
        from(bucket: "{self.bucket}")
            |> range(start: {start}{stop_clause})
            |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            |> filter(fn: (r) => {fields_filter})
        '''
        return query

    def get_latest_measurements(self, measurement: str, fields: List[str]) -> Dict:
        df = self.query_data(measurement, fields, start="-1m")
        if df.empty:
            return {}
        
        latest = df.sort_values("_time", ascending=False).iloc[0]
        return {field: latest.get(field, latest.get("_value")) for field in fields}


if __name__ == "__main__":
    service = InfluxDBService()
    try:
        service.connect()
    except Exception as e:
        print(f"Could not connect to InfluxDB: {e}")
        print("This is expected if InfluxDB is not running locally.")
