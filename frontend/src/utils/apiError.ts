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

  if (Array.isArray(detail)) {
    return detail.map(item => `${Array.isArray(item.loc) ? item.loc.filter((part: unknown) => part !== "body").join(".") : "Input"}: ${typeof item.msg === "string" ? item.msg : "Invalid value"}`).join("; ");
  }

  if (!error.response) return "Unable to reach the server. Please try again.";

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

    case 429:
      return "Too many requests. Please wait and try again.";

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