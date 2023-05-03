# ============================= CLASSES ===================================== #
TIME_FORMAT = u"%Y-%m-%d %H:%M:%S"
class IP(object):
    """
    IP dataclass
    """
    def __init__(self, raw_data=None, isPublic=None, ipVersion=None,
                 isWhitelisted=None, abuseConfidenceScore=None, countryCode=None,
                 countryName=None, usageType=None, isp=None, domain=None, hostnames=None, totalReports=None, numDistinctUsers=None, lastReportedAt=None, reports=None):
        self.raw_data = raw_data
        self.isPublic = isPublic
        self.ipVersion = ipVersion
        self.isWhitelisted = isWhitelisted
        self.abuseConfidenceScore = abuseConfidenceScore
        self.countryCode = countryCode
        self.countryName = countryName
        self.usageType = usageType
        self.isp = isp
        self.domain = domain
        self.hostnames = hostnames
        self.totalReports = totalReports
        self.numDistinctUsers = numDistinctUsers
        self.lastReportedAt = lastReportedAt
        self.reports = reports
    def to_enrichment_data(self):
        return {
            u'countryName': self.countryName,
            u'abuseConfidenceScore': self.abuseConfidenceScore,
            u'domain': self.domain
        }
    def to_json(self):
        return self.raw_data