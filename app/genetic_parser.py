
"""
Nutrigenomics Genetic Parser
============================
Parses 23andMe/AncestryDNA raw data files and extracts diet-relevant genetic variants.

Author: Caraman (Bachelor Thesis Project)
Date: December 2024
Updated: December 2024 - Expanded to 25 SNPs
"""

from snps import SNPs
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum


class RiskLevel(Enum):
    """Risk assessment levels for genetic variants"""
    LOW = "low"
    MODERATE = "moderate" 
    HIGH = "high"
    PROTECTIVE = "protective"


@dataclass
class GeneticVariant:
    """Represents a single genetic variant with its interpretation"""
    rsid: str
    gene: str
    condition: str
    genotype: Optional[str]
    risk_level: RiskLevel
    interpretation: str
    dietary_recommendation: str
    scientific_source: str


# ============================================
# NUTRIGENOMICS SNP DATABASE - 25 VARIANTS
# ============================================

NUTRIGENOMICS_SNPS = {
    
    # ==========================================
    # SECTION 1: DIGESTIVE & FOOD TOLERANCE (4)
    # ==========================================
    
    # 1. LACTOSE INTOLERANCE
    "rs4988235": {
        "gene": "LCT/MCM6",
        "condition": "Lactose Intolerance",
        "category": "digestion",
        "interpretations": {
            "TT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Lactase persistent - you can digest dairy normally",
                "recommendation": "No dairy restrictions needed based on this gene."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate lactase persistence (~65% enzyme activity)",
                "recommendation": "You may tolerate moderate dairy. Monitor for bloating, gas, or discomfort."
            },
            "CC": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Lactase non-persistent - likely lactose intolerant",
                "recommendation": "Consider lactose-free dairy, lactase supplements, or plant-based milk."
            },
            "AA": {
                "risk": RiskLevel.LOW,
                "interpretation": "Lactase persistent (minus strand)",
                "recommendation": "No dairy restrictions needed."
            },
            "AG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate lactase persistence (minus strand)",
                "recommendation": "Monitor for dairy-related symptoms."
            },
            "GG": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Lactase non-persistent (minus strand)",
                "recommendation": "Consider lactose-free alternatives."
            }
        },
        "source": "SNPedia rs4988235; PMID: 15114531"
    },
    
    # 2. CELIAC DISEASE RISK (HLA-DQ2.5)
    "rs2187668": {
        "gene": "HLA-DQ2.5",
        "condition": "Celiac Disease Risk",
        "category": "digestion",
        "interpretations": {
            "TT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Does not carry HLA-DQ2.5 risk allele",
                "recommendation": "Low genetic risk for celiac disease. This does not rule out gluten sensitivity."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Carrier of one HLA-DQ2.5 risk allele",
                "recommendation": "Moderate celiac risk. If you have digestive issues, consider celiac testing."
            },
            "CC": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Homozygous for HLA-DQ2.5 risk allele",
                "recommendation": "Higher celiac risk. Get tested if you have symptoms. Do NOT eliminate gluten before testing."
            },
            "AA": {"risk": RiskLevel.LOW, "interpretation": "Low celiac risk (minus strand)", "recommendation": "Low genetic risk for celiac."},
            "AG": {"risk": RiskLevel.MODERATE, "interpretation": "Moderate celiac risk (minus strand)", "recommendation": "Consider testing if symptomatic."},
            "GG": {"risk": RiskLevel.HIGH, "interpretation": "Higher celiac risk (minus strand)", "recommendation": "Consider celiac testing if symptomatic."}
        },
        "source": "SNPedia rs2187668; PMID: 18311140"
    },
    
    # 3. BITTER TASTE PERCEPTION
    "rs1726866": {
        "gene": "TAS2R38",
        "condition": "Bitter Taste Perception",
        "category": "taste",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Non-taster - reduced sensitivity to bitter compounds (PTC/PROP)",
                "recommendation": "You may find bitter vegetables (broccoli, kale, Brussels sprouts) more palatable. Include them regularly for their health benefits."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Medium taster - moderate bitter sensitivity",
                "recommendation": "You have average bitter taste sensitivity. Cooking methods like roasting can reduce bitterness in vegetables."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Super-taster - highly sensitive to bitter compounds",
                "recommendation": "You may avoid healthy bitter vegetables. Try masking bitterness with olive oil, garlic, or cheese. Roasting reduces bitterness."
            },
            "GG": {"risk": RiskLevel.LOW, "interpretation": "Non-taster (minus strand)", "recommendation": "Bitter vegetables should be easy to enjoy."},
            "AG": {"risk": RiskLevel.MODERATE, "interpretation": "Medium taster (minus strand)", "recommendation": "Average bitter sensitivity."},
            "AA": {"risk": RiskLevel.HIGH, "interpretation": "Super-taster (minus strand)", "recommendation": "Try cooking methods to reduce vegetable bitterness."}
        },
        "source": "PMID: 12595690; SNPedia rs1726866"
    },
    
    # 4. FAT TASTE SENSITIVITY
    "rs1761667": {
        "gene": "CD36",
        "condition": "Fat Taste Sensitivity",
        "category": "taste",
        "interpretations": {
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal fat taste sensitivity",
                "recommendation": "You can detect fat in foods normally, which helps regulate fat intake naturally."
            },
            "AG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced fat taste sensitivity",
                "recommendation": "You may have slightly reduced ability to taste fat, potentially leading to higher fat consumption."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Low fat taste sensitivity",
                "recommendation": "You may not taste fat well, leading to overconsumption. Be mindful of portion sizes for fatty foods."
            }
        },
        "source": "PMID: 21697823; SNPedia rs1761667"
    },
    
    # ==========================================
    # SECTION 2: CAFFEINE & ALCOHOL (3)
    # ==========================================
    
    # 5. CAFFEINE METABOLISM
    "rs762551": {
        "gene": "CYP1A2",
        "condition": "Caffeine Metabolism",
        "category": "metabolism",
        "interpretations": {
            "AA": {
                "risk": RiskLevel.LOW,
                "interpretation": "Fast caffeine metabolizer",
                "recommendation": "You process caffeine quickly. 3-4 cups of coffee/day is generally safe. May have cardiovascular benefits."
            },
            "AC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate caffeine metabolizer",
                "recommendation": "Limit to 1-2 cups coffee/day. Avoid caffeine after 2 PM."
            },
            "CA": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate caffeine metabolizer",
                "recommendation": "Limit to 1-2 cups coffee/day. Avoid caffeine after 2 PM."
            },
            "CC": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Slow caffeine metabolizer",
                "recommendation": "Limit to 1 cup coffee before noon. Slow metabolism increases heart disease risk with high caffeine intake."
            }
        },
        "source": "PMID: 16522833; SNPedia rs762551"
    },
    
    # 6. ALCOHOL FLUSH REACTION
    "rs671": {
        "gene": "ALDH2",
        "condition": "Alcohol Flush Reaction",
        "category": "metabolism",
        "interpretations": {
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal alcohol metabolism (functional ALDH2 enzyme)",
                "recommendation": "You metabolize alcohol normally. Standard alcohol guidelines apply (moderation)."
            },
            "AG": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Reduced ALDH2 activity - alcohol flush reaction",
                "recommendation": "You likely experience facial flushing with alcohol. Increased esophageal cancer risk with regular drinking. Limit alcohol significantly."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Very low ALDH2 activity - severe alcohol intolerance",
                "recommendation": "Strong alcohol intolerance. Even small amounts cause flushing and nausea. Avoid alcohol - significantly increased cancer risk."
            }
        },
        "source": "PMID: 24671021; SNPedia rs671"
    },
    
    # 7. ALCOHOL DEPENDENCE RISK
    "rs1229984": {
        "gene": "ADH1B",
        "condition": "Alcohol Metabolism Speed",
        "category": "metabolism",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Slow alcohol metabolism - typical for most Europeans",
                "recommendation": "Standard alcohol metabolism. Follow general moderation guidelines."
            },
            "CT": {
                "risk": RiskLevel.PROTECTIVE,
                "interpretation": "Faster alcohol metabolism - may be protective against alcoholism",
                "recommendation": "You metabolize alcohol faster, which may reduce risk of alcohol dependence."
            },
            "TT": {
                "risk": RiskLevel.PROTECTIVE,
                "interpretation": "Very fast alcohol metabolism - protective effect",
                "recommendation": "Very fast alcohol metabolism. Associated with lower risk of alcohol dependence."
            }
        },
        "source": "PMID: 21115004; SNPedia rs1229984"
    },
    
    # ==========================================
    # SECTION 3: VITAMINS & MINERALS (8)
    # ==========================================
    
    # 8. FOLATE METABOLISM (MTHFR C677T)
    "rs1801133": {
        "gene": "MTHFR",
        "condition": "Folate Metabolism (C677T)",
        "category": "vitamins",
        "interpretations": {
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal MTHFR enzyme activity (100%)",
                "recommendation": "Normal folate metabolism. Standard dietary folate intake is sufficient."
            },
            "AG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced MTHFR activity (~65%)",
                "recommendation": "Increase leafy greens, legumes, and fortified foods. Consider methylfolate supplement."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly reduced MTHFR activity (~30%)",
                "recommendation": "Prioritize methylfolate (not folic acid). Eat folate-rich foods daily. Consider B-complex with methylated B vitamins."
            },
            "CC": {"risk": RiskLevel.LOW, "interpretation": "Normal MTHFR (minus strand)", "recommendation": "Normal folate metabolism."},
            "CT": {"risk": RiskLevel.MODERATE, "interpretation": "Reduced MTHFR (minus strand)", "recommendation": "Consider methylfolate."},
            "TT": {"risk": RiskLevel.HIGH, "interpretation": "Low MTHFR activity (minus strand)", "recommendation": "Prioritize methylated B vitamins."}
        },
        "source": "PMID: 24494987; SNPedia rs1801133"
    },
    
    # 9. FOLATE METABOLISM (MTHFR A1298C)
    "rs1801131": {
        "gene": "MTHFR",
        "condition": "Folate Metabolism (A1298C)",
        "category": "vitamins",
        "interpretations": {
            "TT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal MTHFR A1298C function",
                "recommendation": "This variant is normal. Check C677T (rs1801133) as well."
            },
            "GT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "One copy of A1298C variant - mild effect",
                "recommendation": "Mild impact on folate. More significant if combined with C677T variant."
            },
            "GG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Two copies of A1298C variant",
                "recommendation": "Reduced BH4 production. May affect neurotransmitter synthesis. Support with methylfolate and B12."
            },
            "AA": {"risk": RiskLevel.LOW, "interpretation": "Normal (minus strand)", "recommendation": "Normal function."},
            "AC": {"risk": RiskLevel.MODERATE, "interpretation": "One variant copy (minus strand)", "recommendation": "Mild impact."},
            "CC": {"risk": RiskLevel.MODERATE, "interpretation": "Two variant copies (minus strand)", "recommendation": "Support with methylated B vitamins."}
        },
        "source": "PMID: 24494987; SNPedia rs1801131"
    },
    
    # 10. VITAMIN B12 ABSORPTION
    "rs602662": {
        "gene": "FUT2",
        "condition": "Vitamin B12 Absorption",
        "category": "vitamins",
        "interpretations": {
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Secretor status - normal B12 absorption",
                "recommendation": "Normal B12 absorption from food. Standard dietary sources sufficient."
            },
            "AG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced secretor status - may have lower B12",
                "recommendation": "May have slightly lower B12 levels. Include B12-rich foods regularly (meat, fish, eggs, dairy)."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Non-secretor - reduced B12 absorption",
                "recommendation": "Higher risk of B12 deficiency. Consider B12 supplements (methylcobalamin). Regular B12 blood tests recommended."
            }
        },
        "source": "PMID: 19303062; SNPedia rs602662"
    },
    
    # 11. VITAMIN B12 METABOLISM (MTRR)
    "rs1801394": {
        "gene": "MTRR",
        "condition": "B12 Utilization",
        "category": "vitamins",
        "interpretations": {
            "AA": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal MTRR function - efficient B12 recycling",
                "recommendation": "Normal B12 utilization. Standard intake sufficient."
            },
            "AG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced MTRR efficiency",
                "recommendation": "May need higher B12 intake. Use methylcobalamin form."
            },
            "GG": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly reduced B12 recycling",
                "recommendation": "Higher B12 requirements. Consider methylcobalamin supplement. Especially important if vegetarian/vegan."
            }
        },
        "source": "PMID: 19116920; SNPedia rs1801394"
    },
    
    # 12. VITAMIN D RECEPTOR
    "rs2228570": {
        "gene": "VDR",
        "condition": "Vitamin D Receptor (FokI)",
        "category": "vitamins",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Optimal VDR function - efficient vitamin D response",
                "recommendation": "Your cells respond well to vitamin D. Maintain adequate intake (sun, food, supplements if needed)."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate VDR function",
                "recommendation": "Slightly reduced vitamin D response. Ensure adequate vitamin D through sun, fatty fish, or supplements."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Reduced VDR function",
                "recommendation": "May need higher vitamin D levels for optimal function. Consider supplements. Test blood levels annually."
            },
            "AA": {"risk": RiskLevel.LOW, "interpretation": "Optimal VDR (minus strand)", "recommendation": "Efficient vitamin D response."},
            "AG": {"risk": RiskLevel.MODERATE, "interpretation": "Intermediate VDR (minus strand)", "recommendation": "Ensure adequate vitamin D."},
            "GG": {"risk": RiskLevel.HIGH, "interpretation": "Reduced VDR (minus strand)", "recommendation": "May need higher vitamin D intake."}
        },
        "source": "PMID: 27188403; SNPedia rs2228570"
    },
    
    # 13. VITAMIN D BINDING PROTEIN
    "rs7041": {
        "gene": "GC",
        "condition": "Vitamin D Transport",
        "category": "vitamins",
        "interpretations": {
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal vitamin D binding protein levels",
                "recommendation": "Normal vitamin D transport. Standard recommendations apply."
            },
            "GT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Slightly lower vitamin D binding protein",
                "recommendation": "May have lower total vitamin D but similar free (active) vitamin D."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Lower vitamin D binding protein",
                "recommendation": "Lower total vitamin D levels common but may not affect free vitamin D. Discuss with doctor if levels are low."
            }
        },
        "source": "PMID: 20541252; SNPedia rs7041"
    },
    
    # 14. VITAMIN C TRANSPORT
    "rs33972313": {
        "gene": "SLC23A1",
        "condition": "Vitamin C Absorption",
        "category": "vitamins",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal vitamin C transporter function",
                "recommendation": "Normal vitamin C absorption. Standard intake from fruits and vegetables is sufficient."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced vitamin C transport efficiency",
                "recommendation": "May benefit from higher vitamin C intake. Include citrus, berries, peppers, and broccoli daily."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly reduced vitamin C absorption",
                "recommendation": "Higher vitamin C requirements. Eat vitamin C-rich foods with every meal. Consider supplements."
            }
        },
        "source": "PMID: 20200966; SNPedia rs33972313"
    },
    
    # 15. IRON ABSORPTION (HFE H63D)
    "rs1799945": {
        "gene": "HFE",
        "condition": "Iron Absorption (H63D)",
        "category": "minerals",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal iron absorption",
                "recommendation": "Standard iron intake appropriate. No genetic predisposition to iron overload."
            },
            "CG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Carrier of H63D variant - slightly increased iron absorption",
                "recommendation": "Mild increased iron absorption. Monitor ferritin levels. Avoid iron supplements unless prescribed."
            },
            "GG": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Homozygous H63D - increased iron absorption risk",
                "recommendation": "Monitor iron and ferritin annually. Avoid iron supplements and excessive red meat. Donate blood if levels are high."
            }
        },
        "source": "PMID: 19159930; SNPedia rs1799945"
    },
    
    # ==========================================
    # SECTION 4: MACRONUTRIENT METABOLISM (6)
    # ==========================================
    
    # 16. OMEGA-3 CONVERSION (FADS1)
    "rs174546": {
        "gene": "FADS1",
        "condition": "Omega-3/6 Fatty Acid Metabolism",
        "category": "fats",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Efficient conversion of plant omega-3 to EPA/DHA",
                "recommendation": "You can convert plant sources (flax, chia, walnuts) to active omega-3s. Still beneficial to eat fatty fish."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate omega-3 conversion ability",
                "recommendation": "Include both plant omega-3s and fatty fish (salmon, sardines, mackerel) 2-3 times per week."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Reduced ability to convert plant omega-3 to EPA/DHA",
                "recommendation": "Prioritize preformed EPA/DHA from fatty fish or algae supplements. Plant sources alone may be insufficient."
            }
        },
        "source": "PMID: 21829377; SNPedia rs174546"
    },
    
    # 17. SATURATED FAT RESPONSE
    "rs5082": {
        "gene": "APOA2",
        "condition": "Saturated Fat Sensitivity",
        "category": "fats",
        "interpretations": {
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal response to saturated fat",
                "recommendation": "Standard saturated fat guidelines apply. Focus on overall diet quality."
            },
            "AG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal response to saturated fat",
                "recommendation": "No special saturated fat restrictions needed."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Increased weight gain with high saturated fat intake",
                "recommendation": "Limit saturated fat to <22g/day. Choose olive oil, avocados, nuts over butter and coconut oil. Keto/Paleo diets may not suit you."
            }
        },
        "source": "PMID: 19858173; SNPedia rs5082"
    },
    
    # 18. CARBOHYDRATE/DIABETES RISK (TCF7L2 - main variant)
    "rs7903146": {
        "gene": "TCF7L2",
        "condition": "Carbohydrate Metabolism / Diabetes Risk",
        "category": "carbs",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal carbohydrate metabolism and insulin secretion",
                "recommendation": "Standard carbohydrate intake is fine. Focus on whole grains and fiber."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Increased Type 2 diabetes risk (~40% higher)",
                "recommendation": "Prioritize low-glycemic carbs. Include protein with meals. Regular exercise helps significantly."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly increased Type 2 diabetes risk (~80% higher)",
                "recommendation": "Limit refined carbs and grains. High-protein, Mediterranean-style diet recommended. Regular blood sugar monitoring advised."
            }
        },
        "source": "PMID: 22693455; SNPedia rs7903146"
    },
    
    # 19. OBESITY RISK / SATIETY (FTO)
    "rs9939609": {
        "gene": "FTO",
        "condition": "Obesity Risk / Satiety",
        "category": "weight",
        "interpretations": {
            "TT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Lower obesity risk - normal satiety signaling",
                "recommendation": "Standard diet and exercise recommendations apply."
            },
            "AT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Moderately increased obesity risk (~30%)",
                "recommendation": "Focus on high-protein, high-fiber meals for satiety. Regular physical activity is especially important."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Increased obesity risk (~70%) - reduced satiety signaling",
                "recommendation": "Prioritize protein and fiber for fullness. Exercise is particularly effective at counteracting this variant. Mindful eating practices help."
            }
        },
        "source": "PMID: 17434869; SNPedia rs9939609"
    },
    
    # 20. PROTEIN/MUSCLE (ACE)
    "rs4341": {
        "gene": "ACE",
        "condition": "Exercise Response / Muscle Type",
        "category": "fitness",
        "interpretations": {
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Higher ACE activity - may favor power/strength activities",
                "recommendation": "May respond well to strength training and high-intensity exercise. Protein timing around workouts may be beneficial."
            },
            "CG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Intermediate ACE activity - balanced response",
                "recommendation": "Balanced response to both endurance and strength training. Varied exercise program recommended."
            },
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Lower ACE activity - may favor endurance activities",
                "recommendation": "May respond better to endurance exercise. Still important to include strength training for muscle maintenance."
            }
        },
        "source": "PMID: 18043716; SNPedia rs4341"
    },
    
    # 21. FAT METABOLISM (APOE - combined with rs429358)
    "rs7412": {
        "gene": "APOE",
        "condition": "Fat Metabolism (APOE e2/e3/e4)",
        "category": "fats",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Part of APOE genotyping - see combined result",
                "recommendation": "This SNP combines with rs429358 to determine APOE type. e3/e3 is most common and neutral."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "May indicate APOE e2 carrier",
                "recommendation": "If APOE e2 carrier: generally favorable for cholesterol but may need higher fat-soluble vitamin intake."
            },
            "TT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "APOE e2/e2 possible",
                "recommendation": "APOE e2 is generally protective for heart disease but may increase triglycerides with high-carb diet."
            }
        },
        "source": "PMID: 24382546; SNPedia rs7412"
    },
    
    # ==========================================
    # SECTION 5: ANTIOXIDANT & DETOX (4)
    # ==========================================
    
    # 22. ANTIOXIDANT CAPACITY (SOD2)
    "rs4880": {
        "gene": "SOD2",
        "condition": "Antioxidant Capacity",
        "category": "antioxidants",
        "interpretations": {
            "AA": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Higher SOD2 in mitochondria - may increase oxidative stress in some contexts",
                "recommendation": "Prioritize antioxidant-rich foods: berries, leafy greens, colorful vegetables. Avoid excessive iron/manganese supplements."
            },
            "AG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Intermediate SOD2 activity",
                "recommendation": "Balanced antioxidant needs. Eat a variety of colorful fruits and vegetables."
            },
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal SOD2 activity",
                "recommendation": "Standard antioxidant intake from diet is sufficient."
            },
            "TT": {"risk": RiskLevel.MODERATE, "interpretation": "Higher SOD2 (minus strand)", "recommendation": "Increase antioxidant intake."},
            "CT": {"risk": RiskLevel.LOW, "interpretation": "Intermediate SOD2 (minus strand)", "recommendation": "Balanced antioxidant needs."},
            "CC": {"risk": RiskLevel.LOW, "interpretation": "Normal SOD2 (minus strand)", "recommendation": "Standard antioxidant intake sufficient."}
        },
        "source": "PMID: 15361839; SNPedia rs4880"
    },
    
    # 23. GLUTATHIONE METABOLISM
    "rs1695": {
        "gene": "GSTP1",
        "condition": "Glutathione Detoxification",
        "category": "detox",
        "interpretations": {
            "AA": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal glutathione S-transferase activity",
                "recommendation": "Normal detoxification capacity. Include cruciferous vegetables for additional support."
            },
            "AG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced detoxification enzyme activity",
                "recommendation": "Increase cruciferous vegetables (broccoli, cauliflower, Brussels sprouts). Support glutathione with sulfur-rich foods."
            },
            "GG": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly reduced GSTP1 activity",
                "recommendation": "Prioritize detox support: cruciferous vegetables, garlic, onions. Consider N-acetyl cysteine (NAC). Minimize toxin exposure."
            }
        },
        "source": "PMID: 19131662; SNPedia rs1695"
    },
    
    # 24. BETA-CAROTENE CONVERSION
    "rs7501331": {
        "gene": "BCMO1",
        "condition": "Beta-Carotene to Vitamin A Conversion",
        "category": "vitamins",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal beta-carotene conversion to vitamin A",
                "recommendation": "You can effectively convert plant sources (carrots, sweet potatoes) to active vitamin A."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced beta-carotene conversion (~32% less)",
                "recommendation": "Include some preformed vitamin A sources (eggs, dairy, liver) alongside plant sources."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly reduced conversion (~69% less)",
                "recommendation": "Relying on beta-carotene alone may lead to vitamin A insufficiency. Include retinol sources: eggs, dairy, fish. Vegans may need retinol supplements."
            }
        },
        "source": "PMID: 19103647; SNPedia rs7501331"
    },
    
    # 25. CHOLINE REQUIREMENTS
    "rs7946": {
        "gene": "PEMT",
        "condition": "Choline Requirements",
        "category": "vitamins",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal endogenous choline production",
                "recommendation": "Standard choline intake is sufficient. Include eggs, liver, or soy regularly."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced ability to produce choline internally",
                "recommendation": "May need more dietary choline. Best sources: eggs (highest), liver, fish, poultry."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly reduced choline synthesis - higher dietary needs",
                "recommendation": "Prioritize choline-rich foods daily: eggs (2/day ideal), liver, fish. Especially important during pregnancy. Consider choline supplement if not eating eggs."
            },
            "GG": {"risk": RiskLevel.LOW, "interpretation": "Normal choline (minus strand)", "recommendation": "Standard intake sufficient."},
            "AG": {"risk": RiskLevel.MODERATE, "interpretation": "Reduced choline production (minus strand)", "recommendation": "Include eggs regularly."},
            "AA": {"risk": RiskLevel.HIGH, "interpretation": "Higher choline needs (minus strand)", "recommendation": "Prioritize eggs and liver."}
        },
        "source": "PMID: 17630398; SNPedia rs7946"
    }
}


# ============================================
# GENETIC PARSER CLASS
# ============================================

class GeneticParser:
    """
    Parses genetic data files and analyzes nutrigenomics variants.
    
    Supports 23andMe, AncestryDNA, and other common formats via the `snps` library.
    
    Usage:
        parser = GeneticParser("genome_file.txt")
        findings = parser.analyze_all()
        print(parser.generate_report())
    """
    
    def __init__(self, filepath: str):
        """
        Initialize the parser with a genetic data file.
        
        Args:
            filepath: Path to 23andMe, AncestryDNA, or similar file
        """
        self.filepath = filepath
        self.snps_data = None
        self.findings = []
        self._load_file()
    
    def _load_file(self):
        """Load and validate the genetic data file"""
        print(f"Loading genetic data from: {self.filepath}")
        print("-" * 50)
        
        self.snps_data = SNPs(self.filepath)
        
        if self.snps_data.snps is None or len(self.snps_data.snps) == 0:
            raise ValueError("No SNP data found in file. Is this a valid genetic data file?")
        
        print(f"[OK] File loaded successfully!")
        print(f"  Source: {self.source}")
        print(f"  Total SNPs: {self.snp_count:,}")
        print(f"  Reference Build: GRCh{self.build}")
        print("-" * 50)
    
    @property
    def source(self) -> str:
        """Get the source company (23andMe, AncestryDNA, etc.)"""
        return self.snps_data.source or "Unknown"
    
    @property
    def snp_count(self) -> int:
        """Total number of SNPs in the file"""
        return len(self.snps_data.snps) if self.snps_data.snps is not None else 0
    
    @property
    def build(self) -> int:
        """Reference genome build (37 or 38)"""
        return self.snps_data.build or 37
    
    def get_genotype(self, rsid: str) -> Optional[str]:
        """
        Get the genotype for a specific rsID.
        
        Args:
            rsid: The SNP identifier (e.g., 'rs4988235')
            
        Returns:
            Genotype string (e.g., 'CT') or None if not found
        """
        if self.snps_data.snps is None:
            return None
        
        try:
            if rsid in self.snps_data.snps.index:
                genotype = self.snps_data.snps.loc[rsid, 'genotype']
                if pd.isna(genotype) or genotype == '--' or genotype == '':
                    return None
                return str(genotype)
        except (KeyError, TypeError):
            pass
        
        return None
    
    def analyze_snp(self, rsid: str) -> GeneticVariant:
        """
        Analyze a single SNP and return its interpretation.
        
        Args:
            rsid: The SNP identifier
            
        Returns:
            GeneticVariant object with interpretation
        """
        if rsid not in NUTRIGENOMICS_SNPS:
            raise ValueError(f"Unknown SNP: {rsid}")
        
        snp_info = NUTRIGENOMICS_SNPS[rsid]
        genotype = self.get_genotype(rsid)
        
        if genotype and genotype in snp_info['interpretations']:
            interp = snp_info['interpretations'][genotype]
            return GeneticVariant(
                rsid=rsid,
                gene=snp_info['gene'],
                condition=snp_info['condition'],
                genotype=genotype,
                risk_level=interp['risk'],
                interpretation=interp['interpretation'],
                dietary_recommendation=interp['recommendation'],
                scientific_source=snp_info['source']
            )
        else:
            return GeneticVariant(
                rsid=rsid,
                gene=snp_info['gene'],
                condition=snp_info['condition'],
                genotype=genotype,
                risk_level=RiskLevel.LOW,
                interpretation=f"Genotype '{genotype}' not in database or not found in your file",
                dietary_recommendation="No specific recommendation available for this genotype.",
                scientific_source=snp_info['source']
            )
    
    def analyze_all(self) -> List[GeneticVariant]:
        """
        Analyze all nutrigenomics SNPs in the database.
        
        Returns:
            List of GeneticVariant objects
        """
        self.findings = []
        
        for rsid in NUTRIGENOMICS_SNPS.keys():
            variant = self.analyze_snp(rsid)
            self.findings.append(variant)
        
        return self.findings
    
    def get_findings_by_risk(self, risk_level: RiskLevel) -> List[GeneticVariant]:
        """Get all findings with a specific risk level"""
        if not self.findings:
            self.analyze_all()
        
        return [f for f in self.findings if f.risk_level == risk_level]
    
    def get_findings_by_category(self, category: str) -> List[GeneticVariant]:
        """Get findings by category (digestion, vitamins, fats, etc.)"""
        if not self.findings:
            self.analyze_all()
        
        category_snps = [rsid for rsid, data in NUTRIGENOMICS_SNPS.items() 
                         if data.get('category') == category]
        
        return [f for f in self.findings if f.rsid in category_snps]
    
    def generate_report(self) -> str:
        """Generate a formatted text report of all findings"""
        if not self.findings:
            self.analyze_all()
        
        lines = []
        lines.append("=" * 60)
        lines.append("   NUTRIGENOMICS ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"\nSource: {self.source}")
        lines.append(f"Total SNPs in file: {self.snp_count:,}")
        lines.append(f"Nutrigenomics variants analyzed: {len(self.findings)}")
        lines.append("")
        
        high_risk = self.get_findings_by_risk(RiskLevel.HIGH)
        moderate_risk = self.get_findings_by_risk(RiskLevel.MODERATE)
        
        if high_risk:
            lines.append("-" * 60)
            lines.append("[!!!] HIGH PRIORITY FINDINGS")
            lines.append("-" * 60)
            for v in high_risk:
                if v.genotype:
                    lines.append(f"\n>> {v.condition} ({v.gene})")
                    lines.append(f"   Genotype: {v.genotype}")
                    lines.append(f"   {v.interpretation}")
                    lines.append(f"   Recommendation: {v.dietary_recommendation}")
        
        if moderate_risk:
            lines.append("\n" + "-" * 60)
            lines.append("[!!] MODERATE PRIORITY FINDINGS")
            lines.append("-" * 60)
            for v in moderate_risk:
                if v.genotype:
                    lines.append(f"\n>> {v.condition} ({v.gene})")
                    lines.append(f"   Genotype: {v.genotype}")
                    lines.append(f"   {v.interpretation}")
        
        lines.append("\n" + "=" * 60)
        lines.append("DISCLAIMER: This report is for educational purposes only.")
        lines.append("Consult a healthcare professional before making dietary changes.")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def export_to_dict(self) -> Dict:
        """Export analysis results as a dictionary (for JSON API responses)"""
        if not self.findings:
            self.analyze_all()
        
        return {
            'file_info': {
                'source': self.source,
                'snp_count': self.snp_count,
                'build': self.build
            },
            'findings': [
                {
                    'rsid': v.rsid,
                    'gene': v.gene,
                    'condition': v.condition,
                    'genotype': v.genotype,
                    'risk_level': v.risk_level.value,
                    'interpretation': v.interpretation,
                    'recommendation': v.dietary_recommendation,
                    'source': v.scientific_source
                }
                for v in self.findings
            ]
        }


# ============================================
# MAIN - Command line testing
# ============================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python genetic_parser.py <genome_file.txt>")
        print("\nThis parser analyzes 25 nutrigenomics variants:")
        
        categories = {}
        for rsid, data in NUTRIGENOMICS_SNPS.items():
            cat = data.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(f"{rsid}: {data['condition']}")
        
        for cat, snps in categories.items():
            print(f"\n  {cat.upper()}:")
            for snp in snps:
                print(f"    - {snp}")
        
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    try:
        parser = GeneticParser(filepath)
        parser.analyze_all()
        print(parser.generate_report())
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)