from typing import List

from pydantic import BaseModel

from src.services.tx_processor import MatchResult, SimplifiedRecord


class StatisticsResponse(BaseModel):
    total_transactions: int
    single_part_transactions: int
    uncategorized_transactions: int
    filtered_by_description_exact: int
    filtered_by_description_partial: int
    not_processed_transactions: int


class UploadResponse(BaseModel):
    message: str
    count: int
    id: str


class ApplyPayload(BaseModel):
    tx_indexes: list[int]


class FilePreviewResponse(BaseModel):
    file_id: str
    decoded_name: str
    size: int
    content: List[SimplifiedRecord]


class FileMatchResponse(BaseModel):
    file_id: str
    decoded_name: str
    records_in_file: int
    transactions_found: int
    transactions_not_matched: int
    transactions_with_one_match: int
    transactions_with_many_matches: int
    content: List[MatchResult]


class FileApplyResponse(BaseModel):
    file_id: str
    updated: int
    errors: List[str]
