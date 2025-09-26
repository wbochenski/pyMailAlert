# pyMailAlert

pyMailAlert is a Python script that monitors data files (CSV or XLSX) for specific conditions and sends email alerts when those conditions are met.

It's designed to help automate data monitoring tasks such as detecting anomalies, missing values, thresholds, or any custom logic using pandas.

# 🔧 Configuration

All configurations are defined in a single .ini file, which consists of two parts:

## 📁 Global Settings

These go under the [config] section:

```ini
[config]
mail_folder=...           # Folder containing mail templates or logs
template_path=...         # Path to your email template (HTML or plain text)
```

## 📂 File Monitoring Sections

Each section below [config] corresponds to a specific set of files to monitor (CSV or XLSX). You can define multiple such sections.

```ini
[<your_section_name>]
type=...                  # Type of file: 'csv' or 'xlsx'
location=...              # Path to the files (wildcards supported)
condition=...             # pandas-compatible condition on the 'table' DataFrame
result=...                # Comma-separated list of columns to include in the result (leave empty for all)
mail_to=...               # IDs to send alerts to
template_path=...         # (optional) Path to email template specific to this section
```

## Example

```ini
[config]
mail_folder=./mails
template_path=./template.html

[SalesThresholdCheck]
type=csv
location=./data/sales_*.csv
condition=table["sales"] > 100000
result=["id", "name", "sales"]
mail_to=["manager"]
```

In this example:

 - The script loads all matching CSV files.
 - It applies the condition: table["sales"] > 100000.
 - If any rows match, it extracts the specified columns (id, name, sales) and sends them via email.

# ✉️ Email Templates

Set template_path in the [config] section to point to your email body template. You can include placeholders like:

```html
Hello,

The following entries matched your condition:

[result]

Regards,  
pyMail
```

The [result] placeholder will be replaced with the filtered DataFrame.

# ✅ Requirements

 - Python 3.7+
 - pandas
 - openpyxl (for Excel files)