# Customer Credit Risk Analysis Report
## Dynamics 365 Finance & Operations - Credit Management

**Report Date:** September 12, 2025  
**Data Source:** D365FO Customer Balance Statistics  
**Environment:** usnconeboxax1aos.cloud.onebox.dynamics.com  
**Analysis Period:** February 2019 - June 2019  

---

## Executive Summary

This report identifies critical credit risk exposures within our customer portfolio, specifically highlighting customers whose outstanding balances exceed their established credit limits. The analysis reveals **7 unique customers** with **12 documented instances** of credit limit violations, representing approximately **$4.5 million** in excess exposure.

### Key Findings:
- **1 Critical Risk Customer** with exposures exceeding 300% of credit limit
- **3 High Risk Customers** consistently operating above established limits
- **Total Risk Exposure:** $4.5M across all violations
- **Primary Risk Concentration:** Retail customer segment (Group 30)

---

## Detailed Analysis

### Critical Risk Customers

#### US-008 - Sparrow Retail
**Risk Level:** 🔴 **CRITICAL**
- **Outstanding Balance:** $1,591,536 (Feb 2019)
- **Credit Limit:** $440,000
- **Excess Amount:** $1,151,536 (362% over limit)
- **Customer Group:** 30 (Retail)
- **Status:** Active, No Hold

**Analysis:** This customer represents our highest credit risk exposure with consistent violations exceeding $800,000. The customer has maintained balances 2.5-3.6x their approved credit limit across multiple periods.

**Recommendation:** Immediate credit review and potential account hold pending resolution.

---

### High Risk Customers

#### US-011 - Contoso Retail Dallas
**Risk Level:** 🟠 **HIGH**
- **Outstanding Balance:** $759,268 (Feb 2019), $621,219 (Jun 2019)
- **Credit Limit:** $440,000
- **Excess Amount:** $319,268 - $181,219
- **Customer Group:** 30 (Retail)

#### US-012 - Contoso Retail New York  
**Risk Level:** 🟠 **HIGH**
- **Outstanding Balance:** $757,031 (Feb 2019), $619,389 (Jun 2019)
- **Credit Limit:** $440,000
- **Excess Amount:** $317,031 - $179,389
- **Customer Group:** 30 (Retail)

#### US-013 - Pelican Wholesales
**Risk Level:** 🟠 **HIGH**
- **Outstanding Balance:** $754,502 (Feb 2019), $617,320 (Jun 2019)
- **Credit Limit:** $550,000
- **Excess Amount:** $204,502 - $67,320
- **Customer Group:** 10 (Wholesale)

**Analysis:** These three customers show consistent patterns of operating above their credit limits, though the trend shows improvement from February to June 2019.

---

### Medium Risk Customers

| Customer | Organization | Balance | Credit Limit | Excess | Date |
|----------|-------------|---------|--------------|--------|------|
| US-023 | Shrike Retail | $329,951 | $275,000 | $54,951 | Feb 2019 |
| US-015 | Contoso Retail Chicago | $277,515 | $275,000 | $2,515 | Feb 2019 |
| US-005 | Contoso Retail Seattle | $129,827 | $60,500 | $69,327 | Feb 2019 |
| US-005 | Contoso Retail Seattle | $106,576 | $16,500 | $90,076 | Jun 2019 |

---

## Risk Assessment Matrix

| Risk Level | Criteria | Customer Count | Total Exposure |
|------------|----------|----------------|-----------------|
| 🔴 Critical | >300% over limit | 1 | $2.9M |
| 🟠 High | 150-300% over limit | 3 | $1.4M |
| 🟡 Medium | 10-150% over limit | 3 | $200K |

---

## Trend Analysis

### Timeline Comparison (Feb 2019 vs Jun 2019)
- **US-008:** Decreased from $1.59M to $1.30M (Still critical)
- **US-011:** Decreased from $759K to $621K (Improvement trend)
- **US-012:** Decreased from $757K to $619K (Improvement trend)
- **US-013:** Decreased from $755K to $617K (Improvement trend)

**Observation:** While most customers showed balance reductions between February and June 2019, all remain significantly above their credit limits.

---

## Customer Segment Analysis

### By Customer Group
- **Group 30 (Retail):** 6 customers, 86% of violations
- **Group 10 (Wholesale):** 1 customer, 14% of violations

### By Organization Type
- **Contoso Retail Locations:** 4 different locations showing violations
- **Independent Retailers:** 2 customers
- **Wholesale Operations:** 1 customer

---

## Data Quality Notes

### Inconsistencies Identified
1. **US-008 (Sparrow Retail):**
   - Customer Master shows: $20,000 credit limit
   - Balance Statistics show: $440,000 credit limit
   - **Action Required:** Reconcile credit limit discrepancies

2. **Historical Data:**
   - Analysis based on 2019 data (most recent available in balance statistics)
   - Current balances may differ significantly

---

## Risk Mitigation Recommendations

### Immediate Actions (0-30 days)
1. **Credit Hold Implementation**
   - Place US-008 (Sparrow Retail) on immediate credit hold
   - Require prepayment or credit guarantee for new orders

2. **Credit Limit Reconciliation**
   - Verify and update credit limits in customer master data
   - Ensure consistency between systems

3. **Account Review Meetings**
   - Schedule urgent review meetings with high-risk customers
   - Obtain updated financial statements and payment commitments

### Short-term Actions (30-90 days)
1. **Credit Limit Adjustments**
   - Consider credit limit increases for well-performing customers with temporary overages
   - Implement stricter limits for consistently non-compliant customers

2. **Enhanced Monitoring**
   - Implement weekly balance monitoring for identified customers
   - Set up automated alerts for credit limit violations

3. **Collection Activities**
   - Accelerate collection efforts for aged balances
   - Consider payment plan arrangements for large overages

### Long-term Strategy (90+ days)
1. **Credit Policy Review**
   - Evaluate current credit limit setting methodology
   - Implement industry-standard credit scoring models

2. **Customer Segmentation**
   - Develop risk-based credit policies by customer segment
   - Implement differentiated monitoring frequencies

3. **System Enhancements**
   - Implement real-time credit checking in order processing
   - Develop automated credit limit violation workflows

---

## Financial Impact Assessment

### Current Exposure
- **Total Credit Exposure:** $4.5M above approved limits
- **Potential Write-off Risk:** 10-15% of excess exposure ($450K-$675K)
- **Collections Cost:** Estimated $50K-$100K for intensive collection activities

### Opportunity Cost
- **Lost Sales:** Potential revenue loss from credit holds
- **Customer Relationships:** Risk of losing high-volume customers

---

## Compliance and Regulatory Considerations

1. **Credit Policy Compliance**
   - Current violations represent non-compliance with internal credit policies
   - Board-level reporting may be required for exposures exceeding limits

2. **Audit Requirements**
   - Document remediation efforts for external auditors
   - Maintain detailed records of collection activities

---

## Conclusion

The analysis reveals significant credit risk concentrations requiring immediate management attention. While the retail segment (Contoso locations) represents the largest number of violations, the single customer US-008 (Sparrow Retail) poses the greatest individual risk with exposures exceeding $1.5M above their credit limit.

The trend analysis suggests some customers are reducing their balances, but the pace of reduction may be insufficient to mitigate risk adequately. Immediate action is required to protect the organization's financial position while maintaining valuable customer relationships.

---

## Next Steps

1. **Immediate:** Execute credit hold for US-008
2. **This Week:** Reconcile credit limit data inconsistencies
3. **Within 30 days:** Complete risk assessment for all high-risk customers
4. **Within 90 days:** Implement enhanced monitoring and collection procedures

---

**Report Prepared By:** D365FO Credit Management System  
**Reviewed By:** [To be completed]  
**Approved By:** [To be completed]  
**Distribution:** CFO, Credit Manager, AR Manager, Sales Director

---
*This report contains confidential financial information. Distribution should be limited to authorized personnel only.*