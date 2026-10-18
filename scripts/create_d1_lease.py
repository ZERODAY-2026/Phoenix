#!/usr/bin/env python3
"""
Create D1_clean_lease.pdf — the benchmark fixture lease.
6-10 pages, numbered clauses covering all 7 required topics.
Fictional landlord name for Phase 6 temp-file leak search.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.colors import black, grey
from reportlab.lib import colors

# ----------------------------------------------------------------------
# Lease content — all fictional, team-written
# ----------------------------------------------------------------------
LANDLORD_NAME = "Aldric Thorne"  # Unique fictional name for Phase 6 leak search
TENANT_NAME = "Marina Voss"
PROPERTY_ADDRESS = "742 Willow Creek Drive, Apartment 3B, Ironwood City, IC 98765"
LEASE_START = "January 1, 2026"
LEASE_END = "December 31, 2026"
MONTHLY_RENT = "$1,850.00"
SECURITY_DEPOSIT = "$3,700.00"
LATE_FEE_AMOUNT = "$75.00"
LATE_FEE_GRACE_DAYS = "5"
NOTICE_PERIOD_DAYS = "60"  # 2 months
DEPOSIT_RETURN_DAYS = "30"

def build_lease_pdf(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.85*inch,
        rightMargin=0.85*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'LeaseTitle',
        parent=styles['Title'],
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    )
    
    subtitle_style = ParagraphStyle(
        'LeaseSubtitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName='Helvetica',
    )
    
    heading_style = ParagraphStyle(
        'ClauseHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        spaceBefore=18,
        spaceAfter=8,
        fontName='Helvetica-Bold',
        textColor=black,
    )
    
    sub_heading_style = ParagraphStyle(
        'SubClauseHeading',
        parent=styles['Heading3'],
        fontSize=11,
        leading=14,
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-BoldOblique',
        textColor=black,
    )
    
    body_style = ParagraphStyle(
        'LeaseBody',
        parent=styles['Normal'],
        fontSize=10.5,
        leading=14,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
    )
    
    body_indent_style = ParagraphStyle(
        'LeaseBodyIndent',
        parent=body_style,
        leftIndent=24,
        firstLineIndent=0,
    )
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=grey,
    )

    story = []

    # ============================================================
    # PAGE 1 — Title & Parties
    # ============================================================
    story.append(Paragraph("RESIDENTIAL LEASE AGREEMENT", title_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Fixed-Term Lease for Dwelling Unit", subtitle_style))
    story.append(Spacer(1, 24))

    # Parties table
    parties_data = [
        ["LANDLORD:", LANDLORD_NAME],
        ["TENANT:", TENANT_NAME],
        ["PREMISES:", PROPERTY_ADDRESS],
        ["LEASE TERM:", f"{LEASE_START} to {LEASE_END} (12 months)"],
        ["MONTHLY RENT:", MONTHLY_RENT],
        ["SECURITY DEPOSIT:", SECURITY_DEPOSIT],
    ]
    
    parties_table = Table(parties_data, colWidths=[1.5*inch, 5*inch])
    parties_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, colors.lightgrey),
    ]))
    story.append(parties_table)
    story.append(Spacer(1, 24))

    story.append(Paragraph("1. PREMISES AND TERM", heading_style))
    story.append(Paragraph(
        f"1.1 The Landlord, {LANDLORD_NAME}, hereby leases to the Tenant, {TENANT_NAME}, "
        f"the residential dwelling unit located at {PROPERTY_ADDRESS} (the \"Premises\"), "
        f"for a fixed term commencing on {LEASE_START} and ending on {LEASE_END} "
        f"(the \"Lease Term\"), unless earlier terminated in accordance with this Agreement.",
        body_style
    ))
    story.append(Paragraph(
        "1.2 The Tenant shall use the Premises solely as a private residence for the Tenant "
        "and the Tenant's immediate family. No business, commercial, or short-term rental "
        "activity (including but not limited to Airbnb, VRBO, or similar platforms) is permitted "
        "without the Landlord's prior written consent.",
        body_style
    ))
    story.append(Paragraph(
        "1.3 The Tenant accepts the Premises in its current condition, \"as-is,\" subject to "
        "the move-in inspection checklist attached as Exhibit A.",
        body_style
    ))

    story.append(PageBreak())

    # ============================================================
    # PAGE 2 — Rent & Payment
    # ============================================================
    story.append(Paragraph("2. RENT AND PAYMENT", heading_style))
    
    story.append(Paragraph("2.1 Monthly Rent", sub_heading_style))
    story.append(Paragraph(
        f"The Tenant shall pay monthly rent of {MONTHLY_RENT} (One Thousand Eight Hundred Fifty "
        "Dollars and Zero Cents) on the first (1st) day of each calendar month during the Lease Term, "
        "in advance, without demand, deduction, or offset. Rent for any partial month shall be prorated "
        "at a daily rate of 1/30th of the monthly rent.",
        body_style
    ))

    story.append(Paragraph("2.2 Payment Method", sub_heading_style))
    story.append(Paragraph(
        "Rent shall be paid by electronic funds transfer to the Landlord's designated account, "
        "or by such other method as the Landlord may specify in writing. The Tenant shall bear any "
        "transaction fees charged by the payment processor.",
        body_style
    ))

    story.append(Paragraph("2.3 Late Fee", sub_heading_style))
    story.append(Paragraph(
        f"If rent is not received in full by the {LATE_FEE_GRACE_DAYS}th day of the month, a late fee "
        f"of {LATE_FEE_AMOUNT} (Seventy-Five Dollars and Zero Cents) shall be assessed. "
        f"An additional late fee of {LATE_FEE_AMOUNT} shall accrue for each subsequent five (5) "
        "calendar days that the rent remains unpaid. Late fees are additional rent and shall be "
        "collectible in the same manner as rent. Acceptance of late payment does not waive the "
        "Landlord's right to enforce timely payment in the future.",
        body_style
    ))

    story.append(Paragraph("2.4 Returned Payment Fee", sub_heading_style))
    story.append(Paragraph(
        "A fee of $35.00 shall be charged for any payment returned for insufficient funds, "
        "stopped payment, or any other reason. This fee is in addition to any late fees that may apply.",
        body_style
    ))

    story.append(PageBreak())

    # ============================================================
    # PAGE 3 — Security Deposit
    # ============================================================
    story.append(Paragraph("3. SECURITY DEPOSIT", heading_style))
    
    story.append(Paragraph("3.1 Amount and Purpose", sub_heading_style))
    story.append(Paragraph(
        f"The Tenant has deposited with the Landlord the sum of {SECURITY_DEPOSIT} "
        "(Three Thousand Seven Hundred Dollars and Zero Cents) as a security deposit "
        "(the \"Deposit\"). The Deposit secures the Tenant's performance of all obligations "
        "under this Agreement, including but not limited to: payment of rent, late fees, and other "
        "charges; repair of damage beyond normal wear and tear; cleaning costs upon move-out; "
        "and any other amounts owed to the Landlord.",
        body_style
    ))

    story.append(Paragraph("3.2 Holding of Deposit", sub_heading_style))
    story.append(Paragraph(
        "The Deposit shall be held in a separate, interest-bearing account in a federally insured "
        "financial institution. The Landlord shall provide the Tenant with the name and address of "
        "the institution and the account number within fourteen (14) days of receipt. Interest "
        "accrued shall belong to the Tenant and shall be paid or credited to the Tenant annually "
        "or upon termination of the tenancy, whichever occurs first.",
        body_style
    ))

    story.append(Paragraph("3.3 Return of Deposit", sub_heading_style))
    story.append(Paragraph(
        f"Within {DEPOSIT_RETURN_DAYS} (thirty) days after the Tenant vacates the Premises and "
        "returns all keys and access devices, the Landlord shall return the Deposit, less any "
        "lawful deductions, together with an itemized written statement of deductions, if any. "
        "Deductions may include: unpaid rent and late fees; costs of repairing damage beyond normal "
        "wear and tear; cleaning costs necessary to restore the Premises to the condition at move-in "
        "(excluding normal wear and tear); and costs of removing abandoned property. If the Landlord "
        "fails to return the Deposit or provide the itemized statement within the thirty (30) day "
        "period, the Tenant may recover the full Deposit plus damages as provided by applicable law.",
        body_style
    ))

    story.append(PageBreak())

    # ============================================================
    # PAGE 4 — Maintenance & Repairs
    # ============================================================
    story.append(Paragraph("4. MAINTENANCE AND REPAIRS", heading_style))
    
    story.append(Paragraph("4.1 Landlord's Obligations", sub_heading_style))
    story.append(Paragraph(
        "The Landlord shall maintain the Premises in a habitable condition and shall make all "
        "repairs necessary to comply with applicable housing codes and to keep the following in "
        "good working order: structural components (roof, walls, floors, foundation); plumbing "
        "systems and fixtures (including pipes, faucets, toilets, water heater); electrical systems "
        "(wiring, outlets, fixtures); heating and ventilation systems; appliances provided by the "
        "Landlord (refrigerator, stove/oven, dishwasher, microwave); and common areas.",
        body_style
    ))

    story.append(Paragraph("4.2 Tenant's Obligations", sub_heading_style))
    story.append(Paragraph(
        "The Tenant shall: keep the Premises clean and sanitary; properly use and operate all "
        "fixtures and appliances; promptly notify the Landlord in writing of any condition requiring "
        "repair; not damage, remove, or alter any part of the Premises; and be liable for any damage "
        "caused by the Tenant, the Tenant's guests, or invitees, beyond normal wear and tear.",
        body_style
    ))

    story.append(Paragraph("4.3 Plumbing Repairs", sub_heading_style))
    story.append(Paragraph(
        "The Landlord is responsible for all plumbing repairs, including but not limited to: "
        "leaking pipes, faucets, and fixtures; clogged drains not caused by the Tenant's misuse; "
        "water heater malfunction; and sewer line issues originating outside the Premises. The "
        "Tenant is responsible for drain clogs caused by foreign objects, grease, hair, or other "
        "materials introduced by the Tenant or the Tenant's guests. The Tenant shall not dispose of "
        "grease, oil, or non-biodegradable materials in any drain or toilet.",
        body_style
    ))

    story.append(Paragraph("4.4 Emergency Repairs", sub_heading_style))
    story.append(Paragraph(
        "In the event of an emergency (gas leak, flooding, no heat in winter, electrical hazard, "
        "or any condition posing immediate danger to health or safety), the Tenant may contact "
        "emergency services directly and shall notify the Landlord as soon as practicable. The "
        "Landlord shall reimburse the Tenant for reasonable emergency repair costs if the Landlord "
        "was unavailable or failed to respond within a reasonable time after notification.",
        body_style
    ))

    story.append(PageBreak())

    # ============================================================
    # PAGE 5 — Pets, Subletting, Utilities
    # ============================================================
    story.append(Paragraph("5. PETS", heading_style))
    
    story.append(Paragraph("5.1 Pet Policy", sub_heading_style))
    story.append(Paragraph(
        "The Tenant may keep one (1) domestic cat or one (1) dog weighing no more than "
        "twenty-five (25) pounds at maturity, subject to the following conditions: (a) the Tenant "
        "shall pay a non-refundable pet fee of $200.00 per pet prior to bringing the animal onto "
        "the Premises; (b) the Tenant shall provide proof of current vaccinations and licensing "
        "as required by local law; (c) the pet shall not create a nuisance (excessive noise, "
        "odors, damage to property, or threat to other residents); (d) the Tenant shall immediately "
        "clean up all pet waste from common areas and the Premises; (e) the Tenant shall be fully "
        "liable for any damage caused by the pet.",
        body_style
    ))

    story.append(Paragraph("5.2 Prohibited Animals", sub_heading_style))
    story.append(Paragraph(
        "The following are prohibited without exception: exotic animals, reptiles, amphibians, "
        "ferrets, birds (except caged birds not exceeding two), livestock, and any animal designated "
        "as dangerous or vicious under applicable law. No additional pets may be acquired without "
        "the Landlord's prior written consent.",
        body_style
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("6. SUBLETTING AND ASSIGNMENT", heading_style))
    story.append(Paragraph(
        "The Tenant shall not sublet the Premises, assign this Agreement, or permit any other person "
        "to occupy the Premises without the Landlord's prior written consent, which consent shall not "
        "be unreasonably withheld. Any request to sublet or assign must be submitted in writing at "
        "least thirty (30) days before the proposed effective date and must include the proposed "
        "subtenant's or assignee's full application, references, and credit information. The original "
        "Tenant remains jointly and severally liable for all obligations under this Agreement "
        "notwithstanding any permitted subletting or assignment. Short-term rentals of any duration "
        "(including but not limited to nightly, weekly, or monthly rentals via any platform) are "
        "strictly prohibited and constitute a material breach of this Agreement.",
        body_style
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("7. UTILITIES AND SERVICES", heading_style))
    story.append(Paragraph(
        "The Tenant shall be responsible for and shall promptly pay all charges for the following "
        "utilities and services supplied to the Premises: electricity, gas, water, sewer, trash "
        "collection, internet, and cable/satellite television. The Landlord shall be responsible "
        "for: property taxes, homeowners association dues (if any), and structural insurance on the "
        "building. The Tenant shall establish all utility accounts in the Tenant's name effective "
        "on the commencement date of the Lease Term and shall not disconnect service before the "
        "termination date. The Landlord makes no representation regarding the availability, quality, "
        "or cost of any utility or service.",
        body_style
    ))

    story.append(PageBreak())

    # ============================================================
    # PAGE 6 — Termination & Notice
    # ============================================================
    story.append(Paragraph("8. TERMINATION", heading_style))
    
    story.append(Paragraph("8.1 Termination by Tenant", sub_heading_style))
    story.append(Paragraph(
        f"The Tenant may terminate this Agreement at the end of the Lease Term or any renewal "
        f"term by giving the Landlord written notice at least {NOTICE_PERIOD_DAYS} (sixty) days "
        "prior to the desired termination date. Such notice must be delivered in accordance with "
        "Section 14 (Notices). If the Tenant fails to give the required notice, the Tenancy shall "
        "convert to a month-to-month tenancy on the same terms, except that the Landlord may "
        "increase the rent upon thirty (30) days' written notice.",
        body_style
    ))

    story.append(Paragraph("8.2 Termination by Landlord", sub_heading_style))
    story.append(Paragraph(
        "The Landlord may terminate this Agreement: (a) at the end of the Lease Term or any "
        "renewal term by giving the Tenant written notice at least sixty (60) days prior to the "
        "termination date; (b) for cause, including but not limited to: material non-compliance "
        "with this Agreement after ten (10) days' written notice to cure (or immediately for "
        "non-payment of rent after the grace period); illegal activity on the Premises; or "
        "substantial damage to the Premises; (c) if the Premises are condemned or rendered "
        "uninhabitable by fire, flood, or other casualty, upon five (5) days' written notice.",
        body_style
    ))

    story.append(Paragraph("8.3 Early Termination Fee", sub_heading_style))
    story.append(Paragraph(
        "If the Tenant terminates this Agreement before the expiration of the Lease Term other "
        "than as permitted by Section 8.2(b) or 8.2(c), the Tenant shall pay an early termination "
        "fee equal to two (2) months' rent ({MONTHLY_RENT} x 2 = $3,700.00) plus all rent due "
        "through the termination date. This fee is liquidated damages, not a penalty, and represents "
        "a reasonable estimate of the Landlord's losses including lost rent, marketing costs, and "
        "administrative expenses.",
        body_style
    ))

    story.append(Paragraph("8.4 Effect of Termination", sub_heading_style))
    story.append(Paragraph(
        "Upon termination, the Tenant shall: vacate the Premises by the termination date; remove "
        "all personal property; clean the Premises to the condition documented in the move-in "
        "inspection checklist (Exhibit A), normal wear and tear excepted; return all keys, access "
        "devices, and parking permits; and provide a forwarding address for the return of the "
        "Deposit. The Landlord's remedies under this Agreement are cumulative and not exclusive.",
        body_style
    ))

    story.append(PageBreak())

    # ============================================================
    # PAGE 7 — Additional Provisions
    # ============================================================
    story.append(Paragraph("9. RENT INCREASES", heading_style))
    story.append(Paragraph(
        "The Landlord may increase the monthly rent upon renewal of the Lease Term by providing "
        "the Tenant with written notice at least sixty (60) days prior to the renewal date. The "
        "increase shall not exceed five percent (5%) of the then-current monthly rent, unless a "
        "greater increase is permitted by applicable law. During the initial Lease Term, the "
        "monthly rent shall not be increased.",
        body_style
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("10. RIGHT OF ENTRY", heading_style))
    story.append(Paragraph(
        "The Landlord may enter the Premises at reasonable times upon twenty-four (24) hours' "
        "written notice for the following purposes: to inspect the Premises; to make necessary "
        "or agreed repairs; to show the Premises to prospective tenants, purchasers, or lenders; "
        "or in case of emergency. The Landlord shall not abuse the right of entry or use it to "
        "harass the Tenant. Entry without notice is permitted only in genuine emergencies.",
        body_style
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("11. INSURANCE", heading_style))
    story.append(Paragraph(
        "The Tenant shall maintain renters insurance with a minimum personal liability coverage of "
        "$100,000.00 and shall name the Landlord as an additional interested party. The Tenant shall "
        "provide proof of insurance to the Landlord within fourteen (14) days of the commencement "
        "date and upon each renewal. The Landlord's insurance does not cover the Tenant's personal "
        "property or liability.",
        body_style
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("12. DEFAULT AND REMEDIES", heading_style))
    story.append(Paragraph(
        "In addition to the late fees specified in Section 2.3, the Landlord may pursue any "
        "remedy available at law or in equity upon the Tenant's default, including but not limited "
        "to: eviction proceedings; recovery of unpaid rent, late fees, and damages; application of "
        "the Deposit; and recovery of attorney's fees and court costs if the Landlord prevails in "
        "any legal action arising from this Agreement. The Tenant's failure to pay rent when due "
        "is a material breach.",
        body_style
    ))

    story.append(PageBreak())

    # ============================================================
    # PAGE 8 — General Provisions & Signatures
    # ============================================================
    story.append(Paragraph("13. GOVERNING LAW AND DISPUTE RESOLUTION", heading_style))
    story.append(Paragraph(
        "This Agreement shall be governed by the laws of the State of Ironwood, without regard to "
        "conflict-of-law principles. Any dispute arising from this Agreement shall first be submitted "
        "to mediation with a mutually agreed mediator. If mediation fails, the dispute shall be "
        "resolved in the courts of Ironwood County. The prevailing party shall be entitled to "
        "reasonable attorney's fees and costs.",
        body_style
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("14. NOTICES", heading_style))
    story.append(Paragraph(
        "All notices under this Agreement must be in writing and shall be deemed delivered: "
        "(a) upon personal delivery; (b) three (3) business days after mailing by certified mail, "
        "return receipt requested; (c) upon confirmed email transmission to the parties' designated "
        "email addresses; or (d) upon confirmed delivery by a nationally recognized overnight courier. "
        "Notices to the Landlord: Aldric Thorne, 1200 Merchant Plaza, Suite 400, Ironwood City, IC 98765, "
        "email: thorne.leases@ironwoodlaw.example. Notices to the Tenant: the Premises address above, "
        "or such other address as the Tenant designates in writing.",
        body_style
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("15. ENTIRE AGREEMENT AND AMENDMENTS", heading_style))
    story.append(Paragraph(
        "This Agreement, including all exhibits and addenda, constitutes the entire agreement "
        "between the parties and supersedes all prior negotiations, understandings, and agreements. "
        "No amendment shall be effective unless in writing, signed by both parties, and expressly "
        "states that it amends this Agreement.",
        body_style
    ))

    story.append(Spacer(1, 12))
    story.append(Paragraph("16. SEVERABILITY", heading_style))
    story.append(Paragraph(
        "If any provision of this Agreement is held invalid or unenforceable, the remaining "
        "provisions shall continue in full force and effect. The parties shall negotiate in good "
        "faith to replace the invalid provision with a valid provision that most closely achieves "
        "the original intent.",
        body_style
    ))

    story.append(Spacer(1, 24))
    story.append(Paragraph("17. SIGNATURES", heading_style))
    story.append(Spacer(1, 12))

    # Signature lines
    sig_data = [
        ["LANDLORD:", "", "TENANT:", ""],
        [LANDLORD_NAME, "Date", TENANT_NAME, "Date"],
        ["________________________________", "___________", "________________________________", "___________"],
    ]
    sig_table = Table(sig_data, colWidths=[2*inch, 1.2*inch, 2*inch, 1.2*inch])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(sig_table)

    story.append(Spacer(1, 36))
    story.append(Paragraph("Exhibit A: Move-In Inspection Checklist (attached)", footer_style))
    story.append(Paragraph("Exhibit B: Rules and Regulations (attached)", footer_style))

    # Build PDF
    doc.build(story)
    print(f"Created {output_path}")


if __name__ == "__main__":
    build_lease_pdf("sample_documents/D1_clean_lease.pdf")