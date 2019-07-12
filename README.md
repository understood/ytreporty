[//]: # (-*- coding: utf-8; mode: Markdown; -*-)

# ytreporty

*ytreporty is currently in pre-alpha.*

ytreporty is a command-line tool and Python package for interfacing
with the [YouTube Reporting API](https://developers.google.com/youtube/reporting/). It manages the API’s
authorization process and provides access to the API’s [resources and
methods](https://developers.google.com/youtube/reporting/v1/reference/rest/). In particular, ytreporty:

- Schedules and deletes reporting jobs with YouTube's reporting
  servers
- Retrieves information about report types, reporting jobs, and
  specific reports
- Fetches individual reports

ytreporty performs these operations by managing authorization
credentials and using standard HTTP requests, performed according to
the [YouTube Reporting API documentation](https://developers.google.com/youtube/reporting/v1/reports/).


## License

[Apache License 2.0](LICENSE)


## Links

- [YouTube Reporting API](https://developers.google.com/youtube/reporting/v1/reports/)
