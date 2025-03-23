import git
from alive_progress import alive_bar


class GitRemoteProgress(git.RemoteProgress):
    """
    A custom Git progress reporter that uses alive_progress for terminal visualization.
    """

    OP_CODES = [
        "BEGIN",
        "CHECKING_OUT",
        "COMPRESSING",
        "COUNTING",
        "END",
        "FINDING_SOURCES",
        "RECEIVING",
        "RESOLVING",
        "WRITING",
    ]
    OP_CODE_MAP = {
        getattr(git.RemoteProgress, code): code for code in OP_CODES
    }

    def __init__(self) -> None:
        super().__init__()
        self.alive_bar_instance = None
        self.bar = None
        self.curr_op = ""

    @classmethod
    def get_curr_op(cls, op_code: int) -> str:
        """
        Convert an op_code to a human-readable operation string.

        Args:
            op_code: Git operation code.

        Returns:
            The name of the current Git operation.
        """
        masked_op = op_code & cls.OP_MASK
        return cls.OP_CODE_MAP.get(masked_op, "Unknown").title()

    def update(
            self,
            op_code: int,
            cur_count: int,
            max_count: int = None,
            message: str = "",
    ) -> None:
        """
        Update the progress bar with the latest Git operation state.

        Args:
            op_code: The current operation code.
            cur_count: Current count of items processed.
            max_count: Total count (if known).
            message: Optional progress message.
        """
        if op_code & self.BEGIN:
            self.curr_op = self.get_curr_op(op_code)
            self._start_bar(self.curr_op)

        if self.bar and max_count and max_count > 0:
            self.bar(cur_count / max_count)
            self.bar.text(message)

        if op_code & self.END:
            self._stop_bar()

    def _start_bar(self, title: str = "") -> None:
        """
        Initialize a new alive progress bar.

        Args:
            title: Title of the progress operation.
        """
        self._stop_bar()  # ensure previous bar is closed
        self.alive_bar_instance = alive_bar(manual=True, title=title)
        self.bar = self.alive_bar_instance.__enter__()

    def _stop_bar(self) -> None:
        """
        Cleanly close the progress bar.
        """
        try:
            if self.alive_bar_instance:
                self.alive_bar_instance.__exit__(None, None, None)
        except Exception:
            pass
        finally:
            self.alive_bar_instance = None
            self.bar = None
