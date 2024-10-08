import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import logging
import details
import utility

def get_recipients():
    """Get email recipients from datasheet"""
    
    data = pd.read_excel("Datasheet.xlsx",sheet_name="Email_Recipients",engine='openpyxl')
    return data["Email"].tolist()

def categories_to_ignore():
    """Get the categories and keywords we want to ignore from datasheet"""
    
    data = pd.read_excel("Datasheet.xlsx",sheet_name="Categories",engine='openpyxl')
    return data["Categories_to_avoid"].tolist()

def send_email(subject, body, to_emails, attachment_data=None, attachment_filename=None, is_xml=False):
    """Send an email with the specified subject and body to the given email addresses."""
    
    from_email = details.email_sender
    password = details.password_email_sender

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = ", ".join(to_emails)
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    # Attach the file if attachment data is provided
    if attachment_data and attachment_filename:
        try:
            part = MIMEBase("application", "octet-stream")

            if is_xml:
                try:
                    xml_content = attachment_data.decode('utf-8')  # Decode the XML content to a string
                    extracted_fields_text = utility.extract_fields_from_xml_content(xml_content)
                    
                    if extracted_fields_text:
                        """Convert the extracted fields to bytes and change the file extension to .txt"""
                        
                        extracted_fields_bytes = extracted_fields_text.encode('utf-8')
                        attachment_data = extracted_fields_bytes  
                        attachment_filename = attachment_filename.replace('.xml', '.txt')

                    else:
                        logging.error("Failed to extract fields from XML content.")
                        return  
                    
                except Exception as e:
                    logging.error(f"Failed to process XML attachment: {e}")
                    return  

            part.set_payload(attachment_data)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {attachment_filename}",
            )
            msg.attach(part)
        except Exception as e:
            logging.error(f"Failed to attach the file: {e}")
            return  

    """Connect to the SMTP server and send the email"""
    
    try:
        with smtplib.SMTP('smtp.gmail.com', 587,timeout=60) as server:  
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        

def send_all_updates(entry, feed_name, entry_data, is_xml, attachment_data=None, attachment_filename=None,send_email_flag=True):
    """Send an email with all the announcements from MongoDB."""
    
    email_recipients = get_recipients()
    
    if not send_email_flag:
        logging.info("Email not sent due to fuzzy logic criteria.")
        return
    
    if feed_name == "NSE_Corporate_Actions":
        if "SERIES:EQ" not in entry.get('summary', ''):
            logging.info("Not Equity")
            return
    
    categories_to_ignore = categories_to_ignore()
    
    if feed_name == "NSE_Corporate_Actions":
        category_match_found = utility.contains_fuzzy_match(entry_data['Purpose'], categories_to_ignore, 80)

        if category_match_found:
            subject = f"{entry.get('title','')} | Purpose:{entry_data["Purpose"]}"
            body = f"\n\nStock: {entry.get('title','')}\nFace Value: {entry_data["Face value"]}\nRecord Date: {entry_data["Record date"]}\nBook Closure Start Date: {entry_data["Book closure start date"]}\nBook Closure End Date: {entry_data["Book closure end date"]}"
            logging.info(f"New Update for {entry.get('title','')}")
            send_email(subject, body, email_recipients, attachment_data, attachment_filename,is_xml)
        else:
            logging.info("No matching category found. Email not sent.")
    
    elif feed_name == "NSE_Financial_Results":       
        subject = f"{entry.get('title','')} | Relating To: {entry_data["Relating to"]} | Period: {entry_data["Period"]} | Period Ended: {entry_data["Period Ended"]}"
        body = f"\n\nStock: {entry.get('title','')}\nRelating To: {entry_data["Relating to"]}\nAudit Status: {entry_data["Audit Status"]}\nCumulative Or Not: {entry_data["Cumulative Or Not"]}\nConsolidated Or Not: {entry_data["Consolidated Or Not"]}\nIND AS Or Not: {entry_data["IND AS Or Not"]}\nPeriod: {entry_data["Period"]}\nPeriod Ended: {entry_data["Period Ended"]}"
        logging.info(f"New Update for {entry.get('title','')}")
        send_email(subject, body, email_recipients, attachment_data, attachment_filename,is_xml)

    elif feed_name == "NSE_Board_Meetings":
        category_match_found = utility.contains_fuzzy_match(entry_data['Purpose'], categories_to_ignore, 80)

        if category_match_found:
            subject = f"{entry.get('title','')} | Purpose: {entry_data["Purpose"]} | Meeting Date:{entry_data["Meeting date"]}"
            body = f"\n\nStock: {entry.get('title','')}\nPurpose: {entry_data["Purpose"]}\nMeeting Date:{entry_data["Meeting date"]}"
            logging.info(f"New Update for {entry.get('title','')}")
            send_email(subject, body, email_recipients, attachment_data, attachment_filename,is_xml)
        else:
            logging.info("No matching category found. Email not sent.")
        
    elif feed_name == "NSE_Company_Announcements":
        category_match_found = utility.contains_fuzzy_match(entry_data['Category'], categories_to_ignore, 80) or utility.contains_fuzzy_match(entry_data["Summary"], categories_to_ignore, 80)

        if category_match_found:
            subject = f"{entry.get('title','')} | Summary: {entry_data["Summary"]}"
            body = f"\n\nStock: {entry.get('title','')}\nCategory: {entry_data["Category"]}\nSummary: {entry_data["Summary"]}"
            logging.info(f"New Update for {entry.get('title','')}")
            send_email(subject, body, email_recipients, attachment_data, attachment_filename,is_xml)
        else:
            logging.info("No matching category found. Email not sent.")
    
    else:
        return
