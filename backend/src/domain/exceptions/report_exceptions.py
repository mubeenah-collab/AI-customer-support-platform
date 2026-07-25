class ReportNotFoundError(Exception):
    """Exception raised when a requested report ID is not found."""

    def __init__(self, report_id: str):
        self.report_id = report_id
        super().__init__(f"Report with ID '{report_id}' was not found.")


class ReportGenerationError(Exception):
    """Exception raised when document summary or report generation fails."""

    def __init__(self, message: str = "Report generation failure"):
        self.message = message
        super().__init__(self.message)
