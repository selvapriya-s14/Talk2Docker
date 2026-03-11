"""
Security scanner for Docker best practices and vulnerabilities.
Checks for common issues in Dockerfiles.
"""

def scan_dockerfile_security(dockerfile_content: str) -> dict:
    """
    Scan a Dockerfile for security issues and best practices.
    Returns dict with findings and severity levels.
    """
    issues = []
    warnings = []
    suggestions = []
    
    content_upper = dockerfile_content.upper()
    
    # CRITICAL: Running as root
    if "USER" not in content_upper:
        issues.append({
            "severity": "CRITICAL",
            "issue": "Running as root",
            "description": "Container runs with root privileges. This is a major security risk.",
            "fix": 'Add "RUN useradd -m -u 1000 appuser && USER appuser" before CMD'
        })
    elif "USER ROOT" in content_upper:
        issues.append({
            "severity": "CRITICAL",
            "issue": "Explicit root user",
            "description": "USER is explicitly set to root.",
            "fix": "Change to a non-root user like 'USER appuser'"
        })
    
    # HIGH: Missing .dockerignore
    if ".DOCKERIGNORE" not in content_upper:
        issues.append({
            "severity": "HIGH",
            "issue": "Missing .dockerignore",
            "description": "No .dockerignore specified. Build context may include unnecessary files.",
            "fix": "Create a .dockerignore file to exclude node_modules, .git, etc."
        })
    
    # HIGH: Running pip/npm without --no-cache
    if "RUN PIP INSTALL" in content_upper and "--NO-CACHE-DIR" not in content_upper:
        issues.append({
            "severity": "HIGH",
            "issue": "Pip cache not cleaned",
            "description": "Pip cache increases image size. Use --no-cache-dir flag.",
            "fix": 'Change to: RUN pip install --no-cache-dir -r requirements.txt'
        })
    
    # HIGH: Using latest tag
    if "FROM" in content_upper:
        lines = dockerfile_content.split('\n')
        for line in lines:
            if line.strip().upper().startswith("FROM"):
                if ":LATEST" in line.upper() or (":LATEST" not in line.upper() and ":" not in line):
                    warnings.append({
                        "severity": "HIGH",
                        "issue": "Unspecified image version",
                        "description": f"'{line.strip()}' uses latest or unversioned image.",
                        "fix": "Specify exact version, e.g., 'python:3.12-slim' or 'node:20-alpine'"
                    })
    
    # MEDIUM: Multiple RUN commands (bad layer caching)
    run_count = content_upper.count("RUN ")
    if run_count > 5:
        suggestions.append({
            "severity": "MEDIUM",
            "issue": "Too many RUN instructions",
            "description": f"Found {run_count} RUN commands. Consider combining with && for fewer layers.",
            "improvement": "Combine RUN commands: RUN apt-get update && apt-get install -y pkg1 pkg2 && rm -rf /var/lib/apt/lists/*"
        })
    
    # MEDIUM: Secrets in COPY/ADD
    if "COPY --CHOWN=" in content_upper or "COPY SECRET" in content_upper:
        warnings.append({
            "severity": "MEDIUM",
            "issue": "Potential secrets in COPY",
            "description": "Avoid copying secret files. Use environment variables or secrets management.",
            "fix": "Use environment variables instead: ENV API_KEY=${API_KEY}"
        })
    
    # MEDIUM: Missing HEALTHCHECK
    if "HEALTHCHECK" not in content_upper:
        suggestions.append({
            "severity": "MEDIUM",
            "issue": "No health check configured",
            "description": "Missing HEALTHCHECK instruction for container monitoring.",
            "improvement": 'Add: HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -f http://localhost:PORT/ || exit 1'
        })
    
    # MEDIUM: apt-get cache not cleaned
    if "APT-GET INSTALL" in content_upper and "RM -RF /VAR/LIB/APT/LISTS" not in content_upper:
        suggestions.append({
            "severity": "MEDIUM",
            "issue": "APT cache not cleaned",
            "description": "apt-get cache not removed. Increases image size.",
            "improvement": "Add 'rm -rf /var/lib/apt/lists/*' after apt-get install"
        })
    
    # LOW: EXPOSE not set
    if "EXPOSE" not in content_upper:
        suggestions.append({
            "severity": "LOW",
            "issue": "No EXPOSE instruction",
            "description": "EXPOSE documents which port the application uses.",
            "improvement": "Add 'EXPOSE 8000' (or appropriate port)"
        })
    
    return {
        "critical_issues": [i for i in issues if i["severity"] == "CRITICAL"],
        "high_issues": [i for i in issues + warnings if i["severity"] == "HIGH"],
        "medium_issues": [i for i in warnings + suggestions if i["severity"] == "MEDIUM"],
        "low_issues": [i for i in suggestions if i["severity"] == "LOW"],
        "summary": {
            "total_critical": len([i for i in issues if i["severity"] == "CRITICAL"]),
            "total_high": len([i for i in issues + warnings if i["severity"] == "HIGH"]),
            "total_medium": len([i for i in warnings + suggestions if i["severity"] == "MEDIUM"]),
            "total_low": len([i for i in suggestions if i["severity"] == "LOW"]),
        }
    }

def format_security_report(scan_results: dict) -> str:
    """Format security scan results for display"""
    report = "🔒 DOCKERFILE SECURITY SCAN\n"
    report += "=" * 80 + "\n\n"
    
    summary = scan_results["summary"]
    total = summary["total_critical"] + summary["total_high"] + summary["total_medium"] + summary["total_low"]
    
    report += f"Total Issues Found: {total}\n"
    report += f"  🔴 Critical: {summary['total_critical']}\n"
    report += f"  🟠 High: {summary['total_high']}\n"
    report += f"  🟡 Medium: {summary['total_medium']}\n"
    report += f"  🔵 Low: {summary['total_low']}\n\n"
    
    # Critical issues
    if scan_results["critical_issues"]:
        report += "🔴 CRITICAL ISSUES (Must Fix):\n"
        for issue in scan_results["critical_issues"]:
            report += f"  • {issue['issue']}\n"
            report += f"    {issue['description']}\n"
            report += f"    Fix: {issue['fix']}\n\n"
    
    # High issues
    if scan_results["high_issues"]:
        report += "🟠 HIGH PRIORITY ISSUES:\n"
        for issue in scan_results["high_issues"]:
            report += f"  • {issue['issue']}\n"
            report += f"    {issue['description']}\n"
            report += f"    Fix: {issue['fix']}\n\n"
    
    # Medium issues
    if scan_results["medium_issues"]:
        report += "🟡 MEDIUM ISSUES (Recommended):\n"
        for issue in scan_results["medium_issues"]:
            report += f"  • {issue.get('issue', 'Improvement')}\n"
            report += f"    {issue.get('description', issue.get('improvement', ''))}\n\n"
    
    return report
