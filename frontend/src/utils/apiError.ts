import axios from "axios";


export function getApiErrorMessage(
  error: unknown
): string {
  if (!axios.isAxiosError(error)) {
    return "An unexpected error occurred.";
  }

  const detail =
    error.response?.data?.detail;

  if (typeof detail === "string") {
    return detail;
  }

  switch (
    error.response?.status
  ) {
    case 401:
      return "Authentication required.";

    case 403:
      return (
        "You do not have permission "
        + "to perform this action."
      );

    case 404:
      return "Resource not found.";

    case 409:
      return "Resource conflict.";

    case 422:
      return (
        "The submitted data "
        + "is invalid."
      );

    case 500:
      return (
        "The server encountered "
        + "an error."
      );

    case 503:
      return (
        "The service is temporarily "
        + "unavailable."
      );

    default:
      return "Request failed.";
  }
}