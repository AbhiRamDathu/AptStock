import pandas as pd
import logging
from io import BytesIO
import re
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class CSVImportService:
    """
    PRODUCTION-READY CSV IMPORT SERVICE

    Handles:
    - Multiple CSV formats (Excel, CSV)
    - Column name detection & normalization
    - Data validation before processing
    - Top products identification
    - Date range detection
    - Sample data extraction
    """

    # ========================================================================
    # COLUMN MAPPING - Handles different POS export formats
    # ========================================================================

    COLUMN_ALIASES = {
        # Date columns
        "date": [
            "date",
            "transaction_date",
            "sales_date",
            "order_date",
            "bill_date",
            "Date",
            "Transaction Date",
            "Sales Date",
        ],
        # Product/Item columns
        "itemname": [
            "product",
            "item",
            "product_name",
            "item_name",
            "productname",
            "itemname",
            "Product",
            "Item Name",
            "Product Name",
        ],
        # SKU/Code columns
        "sku": [
            "sku",
            "product_id",
            "itemcode",
            "item_code",
            "product_code",
            "barcode",
            "SKU",
            "Product ID",
            "Item Code",
        ],
        # Quantity columns
        "quantity": [
            "qty",
            "quantity",
            "units",
            "units_sold",
            "quantity_sold",
            "amount_units",
            "Qty",
            "Units",
            "Units Sold",
            "Quantity",
        ],
        # Price columns (optional)
        "unit_price": [
            "unit_price",
            "price",
            "selling_price",
            "rate",
            "unit_rate",
            "Unit Price",
            "Price",
            "Rate",
        ],
        "amount": [
            "amount",
            "total",
            "sale_amount",
            "total_amount",
            "Amount",
            "Total",
        ],
    }

    @staticmethod
    def detect_column(df: pd.DataFrame, standard_col: str) -> Optional[str]:
        """
        Detect column in DataFrame using alias mapping.
        Returns actual column name in df or None.
        """
        if standard_col not in CSVImportService.COLUMN_ALIASES:
            return None

        df_cols_normalized = (
            df.columns.str.strip().str.lower().str.replace(" ", "_")
        )

        for alias in CSVImportService.COLUMN_ALIASES[standard_col]:
            alias_normalized = alias.lower().replace(" ", "_")
            if alias_normalized in df_cols_normalized.values:
                idx = list(df_cols_normalized).index(alias_normalized)
                return df.columns[idx]

        return None

    @staticmethod
    def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize DataFrame columns and data types.
        """
        df = df.copy()
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )
        logger.info(f"Original columns: {df.columns.tolist()}")
        return df

    @staticmethod
    def parse_csv(file_contents: bytes, filename: str) -> Tuple[pd.DataFrame, List[str]]:
        """
        Parse CSV/Excel file.

        Returns (df, errors_list).
        """
        errors: List[str] = []

        try:
            if filename.endswith(".csv"):
                df = pd.read_csv(BytesIO(file_contents))
            elif filename.endswith((".xlsx", ".xls")):
                df = pd.read_excel(BytesIO(file_contents))
            else:
                raise ValueError(f"Unsupported file format: {filename}")

            logger.info(
                f"Parsed {filename}: {df.shape[0]} rows × {df.shape[1]} columns"
            )

            if df.empty:
                errors.append("File is empty")
                return df, errors

            if len(df) < 2:
                errors.append("File has less than 2 rows")
                return df, errors

            return df, errors

        except Exception as e:
            logger.error(f"Parse error: {e}")
            errors.append(f"Failed to parse file: {e}")
            return pd.DataFrame(), errors

    @staticmethod
    def generate_preview(df: pd.DataFrame) -> Dict:
        """
        Generate preview data from DataFrame.

        Returns:
        - recordCount
        - columns
        - detected_columns
        - dateRange
        - topProducts
        - samples
        - message
        """
        preview: Dict = {
            "recordCount": len(df),
            "columns": df.columns.tolist(),
            "detected_columns": {},
            "dateRange": {},
            "topProducts": [],
            "samples": [],
            "message": "",
        }

        try:
            # 1) Detect standard columns
            date_col = CSVImportService.detect_column(df, "date")
            item_col = CSVImportService.detect_column(df, "itemname")
            sku_col = CSVImportService.detect_column(df, "sku")
            qty_col = CSVImportService.detect_column(df, "quantity")

            logger.info("Detected columns:")
            logger.info(f"  date: {date_col}")
            logger.info(f"  item: {item_col}")
            logger.info(f"  sku: {sku_col}")
            logger.info(f"  qty: {qty_col}")

            if date_col:
                preview["detected_columns"]["date"] = date_col
            if item_col:
                preview["detected_columns"]["itemname"] = item_col
            if sku_col:
                preview["detected_columns"]["sku"] = sku_col
            if qty_col:
                preview["detected_columns"]["quantity"] = qty_col

            # 2) Date range
            if date_col:
                try:
                    df_temp = df.copy()
                    df_temp[date_col] = pd.to_datetime(
                        df_temp[date_col], errors="coerce"
                    )
                    valid_dates = df_temp[date_col].dropna()
                    if len(valid_dates) > 0:
                        min_date = valid_dates.min()
                        max_date = valid_dates.max()
                        preview["dateRange"] = {
                            "start": min_date.strftime("%Y-%m-%d"),
                            "end": max_date.strftime("%Y-%m-%d"),
                        }
                        logger.info(
                            f"Date range: {preview['dateRange']['start']} to {preview['dateRange']['end']}"
                        )
                except Exception as e:
                    logger.warning(f"Could not parse dates: {e}")
                    preview["dateRange"] = {"start": "N/A", "end": "N/A"}

            # 3) Top products
            if qty_col and item_col:
                try:
                    df_temp = df.copy()
                    df_temp[qty_col] = pd.to_numeric(
                        df_temp[qty_col], errors="coerce"
                    )
                    product_sales = (
                        df_temp.groupby(item_col)[qty_col].sum().nlargest(5)
                    )
                    preview["topProducts"] = [
                        {"name": str(name).strip(), "sales": int(sales)}
                        for name, sales in product_sales.items()
                    ]
                    logger.info(
                        f"Top products: {len(preview['topProducts'])} items"
                    )
                except Exception as e:
                    logger.warning(f"Could not compute top products: {e}")

            # 4) Sample rows
            try:
                sample_rows = df.head(5).to_dict("records")
                preview["samples"] = [
                    {k: str(v)[:50] for k, v in row.items()}
                    for row in sample_rows
                ]
                logger.info(f"Sample rows: {len(preview['samples'])}")
            except Exception as e:
                logger.warning(f"Could not build samples: {e}")

            # 5) Message
            preview["message"] = (
                f"Preview ready: {preview['recordCount']} records, "
                f"{len(preview['columns'])} columns, "
                f"{len(preview['topProducts'])} top products detected"
            )
            logger.info(f"PREVIEW COMPLETE: {preview['message']}")

        except Exception as e:
            logger.error(f"Preview generation error: {e}")
            preview["message"] = f"Preview error: {e}"

        return preview

    @staticmethod
    def validate_csv(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate CSV for required logical columns.

        Returns (is_valid, errors_list).
        """
        errors: List[str] = []

        try:
            required = ["date", "itemname", "sku", "quantity"]
            found: List[str] = []

            for req in required:
                detected = CSVImportService.detect_column(df, req)
                if detected:
                    found.append(req)
                else:
                    errors.append(f"Missing required column: {req}")

            valid = len(errors) == 0
            if valid:
                logger.info(f"CSV validation passed. Found: {found}")
            else:
                logger.error(f"CSV validation failed: {errors}")
            return valid, errors

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, [str(e)]
