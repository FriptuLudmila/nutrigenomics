"""
Nutrigenomics Genetic Parser
============================
Parses 23andMe/AncestryDNA raw data files and extracts diet-relevant genetic variants.

Author: Caraman (Bachelor Thesis Project)
Date: December 2024
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
# NUTRIGENOMICS SNP DATABASE
# ============================================
# This is your "knowledge base" - the core of your recommendation system
# Each entry maps an rsID to its interpretation rules

NUTRIGENOMICS_SNPS = {
    # LACTOSE INTOLERANCE
    "rs4988235": {
        "gene": "LCT/MCM6",
        "condition": "Lactose Intolerance",
        "interpretations": {
            "TT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Lactase persistent - you can digest dairy normally",
                "recommendation": "No dairy restrictions needed based on this gene."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate lactase persistence (~65% enzyme activity)",
                "recommendation": "You may tolerate moderate dairy. Monitor for bloating, gas, or discomfort after consuming dairy products."
            },
            "CC": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Lactase non-persistent - likely lactose intolerant",
                "recommendation": "Consider lactose-free dairy alternatives, lactase enzyme supplements before dairy, or plant-based milk (oat, almond, soy)."
            },
            # 23andMe sometimes reports on opposite strand (A/G instead of T/C)
            "AA": {
                "risk": RiskLevel.LOW,
                "interpretation": "Lactase persistent (reported on minus strand)",
                "recommendation": "No dairy restrictions needed based on this gene."
            },
            "AG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate lactase persistence (reported on minus strand)",
                "recommendation": "You may tolerate moderate dairy. Monitor for symptoms."
            },
            "GG": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Lactase non-persistent (reported on minus strand)",
                "recommendation": "Consider lactose-free alternatives or lactase supplements."
            }
        },
        "source": "SNPedia rs4988235; PMID: 15114531"
    },
    
    # CAFFEINE METABOLISM
    "rs762551": {
        "gene": "CYP1A2",
        "condition": "Caffeine Metabolism",
        "interpretations": {
            "AA": {
                "risk": RiskLevel.LOW,
                "interpretation": "Fast caffeine metabolizer",
                "recommendation": "You process caffeine quickly. 3-4 cups of coffee per day is generally safe. Caffeine may even have cardiovascular benefits for fast metabolizers."
            },
            "AC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate caffeine metabolizer",
                "recommendation": "Moderate caffeine intake recommended (1-2 cups coffee/day). Avoid caffeine after 2 PM to prevent sleep disruption."
            },
            "CA": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate caffeine metabolizer",
                "recommendation": "Moderate caffeine intake recommended (1-2 cups coffee/day). Avoid caffeine after 2 PM."
            },
            "CC": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Slow caffeine metabolizer",
                "recommendation": "Limit to 1 cup of coffee per day. Avoid caffeine after noon. Slow metabolizers have increased risk of hypertension and heart issues with high caffeine intake."
            }
        },
        "source": "CYP1A2 polymorphism; PMID: 16522833"
    },
    
    # ALCOHOL METABOLISM
    "rs671": {
        "gene": "ALDH2",
        "condition": "Alcohol Flush Reaction",
        "interpretations": {
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal ALDH2 enzyme activity",
                "recommendation": "Normal alcohol metabolism. Standard alcohol guidelines apply (moderate consumption if you choose to drink)."
            },
            "GA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Reduced ALDH2 activity (~50%) - 'Asian flush' carrier",
                "recommendation": "IMPORTANT: You have 4-8x increased risk of esophageal cancer if you drink alcohol regularly. Facial flushing after drinking is a warning sign. Strongly consider avoiding alcohol or limiting to rare occasions."
            },
            "AG": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Reduced ALDH2 activity (~50%)",
                "recommendation": "Same as GA - significantly elevated cancer risk with alcohol consumption. Consider avoiding alcohol."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Very low ALDH2 activity (1-4%)",
                "recommendation": "AVOID ALCOHOL. You lack the enzyme to properly process acetaldehyde, a toxic alcohol byproduct. Even small amounts cause severe reactions and health risks."
            }
        },
        "source": "ALDH2*2 variant; PMID: 19706858"
    },
    
    # FOLATE METABOLISM (MTHFR)
    "rs1801133": {
        "gene": "MTHFR",
        "condition": "Folate Metabolism (C677T)",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal MTHFR enzyme activity (100%)",
                "recommendation": "Standard folic acid from diet and supplements works well for you."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced MTHFR activity (~65%)",
                "recommendation": "Consider methylfolate (L-5-MTHF) supplements instead of regular folic acid. Increase leafy greens, legumes, and fortified foods."
            },
            "TC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced MTHFR activity (~65%)",
                "recommendation": "Consider methylfolate supplements. Increase folate-rich foods."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly reduced MTHFR activity (~30%)",
                "recommendation": "STRONGLY recommend methylfolate (L-5-MTHF) instead of folic acid. Your body has difficulty converting regular folic acid to its active form. Also consider B12 (methylcobalamin) supplementation. Eat folate-rich foods: spinach, asparagus, broccoli, legumes."
            },
            # Opposite strand reporting
            "GG": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal MTHFR activity (opposite strand)",
                "recommendation": "Standard folic acid works well for you."
            },
            "GA": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced MTHFR activity (opposite strand)",
                "recommendation": "Consider methylfolate supplements."
            },
            "AG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Reduced MTHFR activity (~65%)",
                "recommendation": "Consider methylfolate (L-5-MTHF) supplements instead of regular folic acid."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Significantly reduced MTHFR activity (opposite strand)",
                "recommendation": "Strongly recommend methylfolate instead of folic acid."
            }
        },
        "source": "MTHFR C677T; PMID: 9545397"
    },
    
    "rs1801131": {
        "gene": "MTHFR",
        "condition": "Folate Metabolism (A1298C)",
        "interpretations": {
            "AA": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal A1298C variant",
                "recommendation": "Normal folate metabolism at this position."
            },
            "AC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "One copy of A1298C variant",
                "recommendation": "Slightly reduced MTHFR function. If combined with C677T heterozygous (compound heterozygote), methylfolate is recommended."
            },
            "CA": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "One copy of A1298C variant",
                "recommendation": "Slightly reduced function. Check your rs1801133 result too."
            },
            "CC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Two copies of A1298C variant",
                "recommendation": "Moderately reduced MTHFR function. Consider methylfolate supplementation."
            },
            # Opposite strand
            "TT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal (opposite strand)",
                "recommendation": "Normal folate metabolism at this position."
            },
            "TG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Heterozygous (opposite strand)",
                "recommendation": "Slightly reduced function."
            },
            "GT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Heterozygous A1298C variant",
                "recommendation": "Slightly reduced MTHFR function. Check your rs1801133 result too."
            },
            "GG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Homozygous variant (opposite strand)",
                "recommendation": "Consider methylfolate supplementation."
            }
        },
        "source": "MTHFR A1298C; PMID: 10090477"
    },
    
    # OMEGA-3 METABOLISM
    "rs174546": {
        "gene": "FADS1",
        "condition": "Omega-3/6 Fatty Acid Metabolism",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Efficient converter of plant omega-3 to EPA/DHA",
                "recommendation": "You can efficiently convert plant-based omega-3s (ALA from flax, chia, walnuts) to active forms (EPA/DHA)."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate omega-3 conversion efficiency",
                "recommendation": "Consider including both plant sources AND direct EPA/DHA sources (fatty fish 2x/week or fish oil supplements)."
            },
            "TC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Intermediate omega-3 conversion",
                "recommendation": "Include direct EPA/DHA sources alongside plant omega-3s."
            },
            "TT": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Reduced omega-3 conversion ability",
                "recommendation": "PRIORITIZE direct EPA/DHA sources: fatty fish (salmon, sardines, mackerel) 2-3x per week, or fish oil/algae oil supplements. Plant omega-3s alone may not be sufficient."
            }
        },
        "source": "FADS1 polymorphism; PMID: 21829377"
    },
    
    # OBESITY/SATIETY
    "rs9939609": {
        "gene": "FTO",
        "condition": "Obesity Risk / Satiety",
        "interpretations": {
            "TT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Lower genetic obesity risk",
                "recommendation": "Standard healthy eating guidelines apply. You may have typical satiety signals."
            },
            "AT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Slightly increased obesity risk",
                "recommendation": "You may benefit from mindful eating practices. Physical activity can significantly offset this genetic tendency. Focus on protein and fiber for satiety."
            },
            "TA": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Slightly increased obesity risk",
                "recommendation": "Mindful eating and regular exercise recommended."
            },
            "AA": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Increased obesity risk (~3kg higher average weight)",
                "recommendation": "IMPORTANT: Regular physical activity can completely neutralize this genetic effect. Focus on: high-protein meals, fiber-rich foods, portion awareness, and consistent exercise. You may feel less full after meals - practice mindful eating."
            }
        },
        "source": "FTO rs9939609; PMID: 17434869"
    },
    
    # IRON METABOLISM
    "rs1799945": {
        "gene": "HFE",
        "condition": "Iron Absorption (H63D)",
        "interpretations": {
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Normal iron absorption",
                "recommendation": "Standard iron intake guidelines apply."
            },
            "CG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "One copy of H63D - slightly increased iron absorption",
                "recommendation": "You may absorb iron more efficiently. Avoid unnecessary iron supplements unless prescribed. Include vitamin C with iron-rich meals for optimal absorption."
            },
            "GC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "H63D heterozygote",
                "recommendation": "Slightly increased iron absorption. Monitor iron levels periodically."
            },
            "GG": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Two copies of H63D",
                "recommendation": "Monitor iron/ferritin levels annually. Avoid iron supplements unless deficient. Blood donation can help maintain healthy iron levels."
            }
        },
        "source": "HFE H63D; PMID: 9462759"
    },
    
    # CELIAC / GLUTEN SENSITIVITY RISK
    "rs2187668": {
        "gene": "HLA-DQ2.5",
        "condition": "Celiac Disease Risk",
        "interpretations": {
            "TT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Lower genetic risk for celiac disease",
                "recommendation": "Lower genetic predisposition to celiac. Note: This does not test for non-celiac gluten sensitivity."
            },
            "CT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Carrier of HLA-DQ2.5 risk allele",
                "recommendation": "You carry one celiac risk allele. If you experience symptoms (bloating, diarrhea, fatigue after eating gluten), consult a doctor for proper celiac testing BEFORE going gluten-free."
            },
            "TC": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "Carrier of celiac risk allele",
                "recommendation": "One celiac risk allele present. See doctor if symptoms occur."
            },
            "CC": {
                "risk": RiskLevel.HIGH,
                "interpretation": "Higher genetic risk for celiac disease",
                "recommendation": "IMPORTANT: You have genetic predisposition to celiac disease. This does NOT mean you have celiac - only that you could develop it. If you have symptoms (digestive issues, fatigue, skin problems), get tested. Do NOT eliminate gluten before testing as it affects results."
            }
        },
        "source": "HLA-DQ2.5; PMID: 18509540"
    },
    
    # VITAMIN D METABOLISM
    "rs2228570": {
        "gene": "VDR",
        "condition": "Vitamin D Receptor",
        "interpretations": {
            "TT": {
                "risk": RiskLevel.MODERATE,
                "interpretation": "May have reduced vitamin D receptor efficiency",
                "recommendation": "You may need higher vitamin D intake. Consider: more sun exposure (safely), vitamin D3 supplements (1000-2000 IU/day), fatty fish, fortified foods. Get levels tested."
            },
            "CT": {
                "risk": RiskLevel.LOW,
                "interpretation": "Intermediate vitamin D receptor function",
                "recommendation": "Standard vitamin D recommendations apply. Consider testing levels seasonally."
            },
            "TC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Intermediate VDR function",
                "recommendation": "Standard recommendations apply."
            },
            "CC": {
                "risk": RiskLevel.LOW,
                "interpretation": "Efficient vitamin D receptor",
                "recommendation": "Your vitamin D receptors function well. Maintain adequate intake through sun, diet, or supplements as needed."
            }
        },
        "source": "VDR FokI; PMID: 10332573"
    }
}


class GeneticParser:
    """
    Main parser class for analyzing genetic raw data files.
    
    Usage:
        parser = GeneticParser("path/to/genome.txt")
        results = parser.analyze_nutrigenomics()
        parser.print_report()
    """
    
    def __init__(self, filepath: str):
        """
        Initialize the parser with a genetic data file.
        
        Args:
            filepath: Path to 23andMe/AncestryDNA raw data file
        """
        self.filepath = filepath
        self.snps_data = None
        self.source = None
        self.snp_count = 0
        self.build = None
        self._load_file()
    
    def _load_file(self):
        """Load and parse the genetic data file using snps library"""
        print(f"Loading genetic data from: {self.filepath}")
        print("-" * 50)
        
        try:
            # Use snps library to parse the file
            s = SNPs(self.filepath)
            
            self.snps_data = s.snps  # pandas DataFrame
            self.source = s.source
            self.snp_count = s.count
            self.build = s.build
            
            print(f"[OK] File loaded successfully!")
            print(f"  Source: {self.source}")
            print(f"  Total SNPs: {self.snp_count:,}")
            print(f"  Reference Build: GRCh{self.build}")
            print("-" * 50)
            
        except Exception as e:
            print(f"[ERROR] Error loading file: {e}")
            raise
    
    def get_genotype(self, rsid: str) -> Optional[str]:
        """
        Get the genotype for a specific SNP.
        
        Args:
            rsid: The reference SNP ID (e.g., 'rs4988235')
            
        Returns:
            Genotype string (e.g., 'CT') or None if not found
        """
        if self.snps_data is None:
            return None
        
        try:
            if rsid in self.snps_data.index:
                genotype = self.snps_data.loc[rsid, 'genotype']
                # Handle missing/no-call genotypes
                if pd.isna(genotype) or genotype == '--':
                    return None
                return str(genotype)
        except (KeyError, TypeError):
            pass
        
        return None
    
    def analyze_snp(self, rsid: str) -> Optional[GeneticVariant]:
        """
        Analyze a single SNP and return its interpretation.
        
        Args:
            rsid: The reference SNP ID
            
        Returns:
            GeneticVariant object with interpretation, or None if not found
        """
        if rsid not in NUTRIGENOMICS_SNPS:
            return None
        
        genotype = self.get_genotype(rsid)
        snp_info = NUTRIGENOMICS_SNPS[rsid]
        
        # Get interpretation based on genotype
        if genotype and genotype in snp_info["interpretations"]:
            interp = snp_info["interpretations"][genotype]
            return GeneticVariant(
                rsid=rsid,
                gene=snp_info["gene"],
                condition=snp_info["condition"],
                genotype=genotype,
                risk_level=interp["risk"],
                interpretation=interp["interpretation"],
                dietary_recommendation=interp["recommendation"],
                scientific_source=snp_info["source"]
            )
        else:
            # SNP not found in user's data or genotype not in our database
            return GeneticVariant(
                rsid=rsid,
                gene=snp_info["gene"],
                condition=snp_info["condition"],
                genotype=genotype,
                risk_level=RiskLevel.LOW,
                interpretation="Genotype not found or not in database",
                dietary_recommendation="Unable to provide specific recommendation - genotype data not available.",
                scientific_source=snp_info["source"]
            )
    
    def analyze_nutrigenomics(self) -> List[GeneticVariant]:
        """
        Analyze all nutrigenomics-relevant SNPs.
        
        Returns:
            List of GeneticVariant objects with interpretations
        """
        results = []
        
        for rsid in NUTRIGENOMICS_SNPS.keys():
            variant = self.analyze_snp(rsid)
            if variant:
                results.append(variant)
        
        return results
    
    def get_high_priority_findings(self) -> List[GeneticVariant]:
        """Get only HIGH and MODERATE risk findings"""
        all_results = self.analyze_nutrigenomics()
        return [v for v in all_results if v.risk_level in [RiskLevel.HIGH, RiskLevel.MODERATE]]
    
    def print_report(self):
        """Print a formatted report of all nutrigenomics findings"""
        results = self.analyze_nutrigenomics()
        
        print("\n" + "=" * 70)
        print("           PERSONALIZED NUTRIGENOMICS REPORT")
        print("=" * 70)
        print(f"\nFile: {self.filepath}")
        print(f"Source: {self.source}")
        print(f"SNPs analyzed: {len(NUTRIGENOMICS_SNPS)}")
        print("\n" + "-" * 70)
        
        # Group by risk level
        high_risk = [v for v in results if v.risk_level == RiskLevel.HIGH]
        moderate_risk = [v for v in results if v.risk_level == RiskLevel.MODERATE]
        low_risk = [v for v in results if v.risk_level == RiskLevel.LOW]
        
        # Print HIGH priority first
        if high_risk:
            print("\n[!!!] HIGH PRIORITY FINDINGS:")
            print("-" * 70)
            for v in high_risk:
                self._print_variant(v)
        
        # Then MODERATE
        if moderate_risk:
            print("\n[!!] MODERATE FINDINGS:")
            print("-" * 70)
            for v in moderate_risk:
                self._print_variant(v)
        
        # Then LOW/NORMAL
        if low_risk:
            print("\n[OK] NORMAL/LOW RISK:")
            print("-" * 70)
            for v in low_risk:
                self._print_variant(v, brief=True)
        
        # Disclaimer
        print("\n" + "=" * 70)
        print("[!] DISCLAIMER")
        print("-" * 70)
        print("This report is for educational purposes only and does not constitute")
        print("medical advice. Genetic predisposition does not guarantee any specific")
        print("outcome. Please consult a healthcare professional or registered")
        print("dietitian before making significant dietary changes.")
        print("=" * 70)
    
    def _print_variant(self, v: GeneticVariant, brief: bool = False):
        """Helper to print a single variant"""
        print(f"\n>> {v.condition} ({v.gene})")
        print(f"   SNP: {v.rsid} | Your genotype: {v.genotype or 'Not found'}")
        
        if not brief:
            print(f"   [i] {v.interpretation}")
            print(f"   [>] Recommendation: {v.dietary_recommendation}")
            print(f"   [source] {v.scientific_source}")
        else:
            print(f"   [ok] {v.interpretation}")
    
    def export_to_dict(self) -> Dict:
        """Export results as a dictionary (for API/JSON responses)"""
        results = self.analyze_nutrigenomics()
        return {
            "file_info": {
                "source": self.source,
                "snp_count": self.snp_count,
                "build": self.build
            },
            "findings": [
                {
                    "rsid": v.rsid,
                    "gene": v.gene,
                    "condition": v.condition,
                    "genotype": v.genotype,
                    "risk_level": v.risk_level.value,
                    "interpretation": v.interpretation,
                    "recommendation": v.dietary_recommendation,
                    "source": v.scientific_source
                }
                for v in results
            ]
        }


# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    # Example usage
    parser = GeneticParser("sample_genome.txt")
    parser.print_report()
    
    # You can also access individual results programmatically:
    print("\n\n--- Programmatic Access Example ---")
    
    # Get just the lactose result
    lactose = parser.analyze_snp("rs4988235")
    if lactose:
        print(f"\nLactose tolerance genotype: {lactose.genotype}")
        print(f"Risk level: {lactose.risk_level.value}")
    
    # Get high priority findings only
    print("\n--- High Priority Findings ---")
    priority = parser.get_high_priority_findings()
    for finding in priority:
        print(f"• {finding.condition}: {finding.genotype} ({finding.risk_level.value})")
