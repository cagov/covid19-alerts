## NOTE: As of 5-28-2024 This project is not actively maintained by ODI and this repo is being converted to Archive (read-only) status.
## The daemons have been disabled.

The daemon utilities in this repository are used for continuous tracking of the COVID-19 website.

They both report to the #covid19-alerts channel on Slack.

CaGovDaemon reports updates to pages and site outages. This service now works off the sitemap.xml file, and shouldn’t need to be tweaked for future page retirements. This bot currently ignores changes to translated pages, but checks everything else.  If > 5 pages have been updated, it just reports the total - this typically happens when a site-wide header/footer has been modified.

ChartChecker reports updates to the summary boxes and state-dashboard charts, typically between 9:15-9:36am. It says the state-dashboard has been ‘fully-updated’ when the numbers in the summary boxes match the numbers in the charts, and the various dates look current.  It also reports to the #covid19-state-dash channel, but not as frequently.

The sample configuration files are  copies of the files used to configure these services, via supervisord, on an Ubuntu server.

The two additional prerequisites needed to run these services on a vanilla Ubuntu installation are
supervisor, and python-lxml, both installable via the apt service.

