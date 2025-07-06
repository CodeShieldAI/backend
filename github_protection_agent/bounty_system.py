"""
Bounty System Module
Handles community-driven infringement reporting with rewards
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

from .utils import setup_logging

logger = setup_logging(__name__)


class BountySystem:
    """Manages the infringement bounty system"""
    
    def __init__(self, blockchain_manager, github_scanner, dmca_generator, ipfs_manager):
        self.blockchain = blockchain_manager
        self.scanner = github_scanner
        self.dmca_gen = dmca_generator
        self.ipfs = ipfs_manager
        
        # Track pending reports
        self.pending_reports = {}
        self.verified_reports = {}
    
    async def submit_infringement_report(self, reporter_address: str, 
                                       original_url: str, 
                                       infringing_url: str,
                                       evidence: Dict) -> Dict:
        """Submit an infringement report for bounty consideration"""
        try:
            logger.info(f"🎯 Processing bounty submission from {reporter_address}")
            
            # Step 1: Verify the original URL is registered
            link_status = self.blockchain.check_link_status(original_url)
            if not link_status.get('exists'):
                return {
                    'success': False,
                    'error': 'Original repository not registered in our system'
                }
            
            # Step 2: Check if infringement already reported
            infringement_status = self.blockchain.check_link_status(infringing_url)
            if infringement_status.get('exists'):
                return {
                    'success': False,
                    'error': 'This infringement has already been reported'
                }
            
            # Step 3: Validate the infringement claim
            validation_result = await self.validate_infringement(
                original_url, 
                infringing_url,
                evidence
            )
            
            if not validation_result['is_valid']:
                return {
                    'success': False,
                    'error': 'Infringement claim could not be validated',
                    'details': validation_result.get('reason')
                }
            
            # Step 4: Generate DMCA notice
            dmca_data = {
                'original_repo': {
                    'github_url': original_url,
                    'license_cid': link_status['license_cid'],
                    'registered_at': datetime.fromtimestamp(link_status['timestamp']).isoformat()
                },
                'infringing_repo': {
                    'url': infringing_url,
                    'name': infringing_url.split('/')[-1]
                },
                'similarity_score': validation_result['similarity_score'],
                'evidence': validation_result['evidence'],
                'timestamp': datetime.now().isoformat(),
                'reporter': reporter_address
            }
            
            # Generate DMCA PDF
            dmca_pdf_path = self.dmca_gen.generate_dmca_pdf(dmca_data)
            
            # Upload to IPFS
            dmca_ipfs_hash = self.ipfs.upload_to_ipfs(dmca_pdf_path)
            
            # Step 5: Submit to blockchain for bounty
            bounty_result = self.blockchain.report_infringement_for_bounty(
                infringing_url,
                link_status['license_cid'],
                dmca_ipfs_hash
            )
            
            if not bounty_result['success']:
                return {
                    'success': False,
                    'error': 'Failed to submit bounty claim',
                    'details': bounty_result.get('error')
                }
            
            # Track the report
            report_id = f"bounty_{bounty_result['tx_hash'][:8]}"
            self.verified_reports[report_id] = {
                'reporter': reporter_address,
                'original_url': original_url,
                'infringing_url': infringing_url,
                'similarity_score': validation_result['similarity_score'],
                'dmca_cid': dmca_ipfs_hash,
                'tx_hash': bounty_result['tx_hash'],
                'timestamp': datetime.now().isoformat(),
                'bounty_amount': '1 FIL'  # Standard bounty
            }
            
            logger.info(f"✅ Bounty report verified and submitted: {report_id}")
            
            return {
                'success': True,
                'report_id': report_id,
                'tx_hash': bounty_result['tx_hash'],
                'dmca_ipfs': dmca_ipfs_hash,
                'dmca_url': self.ipfs.get_ipfs_url(dmca_ipfs_hash),
                'bounty_amount': '1 FIL',
                'message': 'Infringement verified! Bounty will be available after transaction confirmation.'
            }
            
        except Exception as e:
            logger.error(f"Bounty submission failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def validate_infringement(self, original_url: str, 
                                  infringing_url: str,
                                  evidence: Dict) -> Dict:
        """Validate an infringement claim using AI and code analysis"""
        try:
            # Use the scanner to compare repositories
            comparison_result = self.scanner.compare_repository_code(
                original_url,
                infringing_url
            )
            
            similarity_score = comparison_result.get('similarity_score', 0)
            
            # Enhanced validation with evidence
            if evidence.get('specific_files'):
                # Check specific files mentioned in evidence
                file_similarities = []
                for file_pair in evidence['specific_files']:
                    # Compare specific files
                    # This would need implementation in github_scanner
                    pass
            
            # AI validation of the claim
            ai_validation = await self._ai_validate_claim(
                original_url,
                infringing_url,
                evidence,
                comparison_result
            )
            
            # Determine if valid (threshold: 70% similarity)
            is_valid = similarity_score >= 0.7 and ai_validation['confidence'] > 0.8
            
            return {
                'is_valid': is_valid,
                'similarity_score': similarity_score,
                'evidence': comparison_result.get('evidence', []),
                'ai_assessment': ai_validation['assessment'],
                'confidence': ai_validation['confidence'],
                'reason': ai_validation.get('reason', '')
            }
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                'is_valid': False,
                'error': str(e)
            }
    
    async def _ai_validate_claim(self, original_url: str, 
                                infringing_url: str,
                                evidence: Dict,
                                comparison_result: Dict) -> Dict:
        """Use AI to validate infringement claim"""
        # This would use the LLM to assess the claim
        # For now, return a mock result
        return {
            'confidence': 0.85,
            'assessment': 'High likelihood of code infringement based on structural similarity',
            'reason': 'Multiple core functions show identical implementation patterns'
        }
    
    def check_reporter_balance(self, address: str) -> Dict:
        """Check bounty balance for a reporter"""
        try:
            balance = self.blockchain.get_bounty_balance(address)
            
            # Get report history
            reporter_reports = [
                report for report_id, report in self.verified_reports.items()
                if report['reporter'] == address
            ]
            
            return {
                'success': True,
                'address': address,
                'balance': balance,
                'balance_fil': f"{balance / 10**18:.4f} FIL",
                'total_reports': len(reporter_reports),
                'reports': reporter_reports
            }
            
        except Exception as e:
            logger.error(f"Balance check failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def withdraw_reporter_bounty(self, address: str) -> Dict:
        """Withdraw bounty rewards for a reporter"""
        try:
            # Verify the caller owns the address
            if self.blockchain.address != address:
                return {
                    'success': False,
                    'error': 'Can only withdraw from your own address'
                }
            
            result = self.blockchain.withdraw_bounty()
            
            if result['success']:
                logger.info(f"💰 Bounty withdrawn: {result['amount']} FIL")
            
            return result
            
        except Exception as e:
            logger.error(f"Withdrawal failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_bounty_leaderboard(self) -> List[Dict]:
        """Get top bounty hunters"""
        reporter_stats = {}
        
        for report in self.verified_reports.values():
            reporter = report['reporter']
            if reporter not in reporter_stats:
                reporter_stats[reporter] = {
                    'address': reporter,
                    'reports': 0,
                    'total_earned': 0
                }
            
            reporter_stats[reporter]['reports'] += 1
            reporter_stats[reporter]['total_earned'] += 1  # 1 FIL per report
        
        # Sort by reports
        leaderboard = sorted(
            reporter_stats.values(),
            key=lambda x: x['reports'],
            reverse=True
        )
        
        return leaderboard[:10]  # Top 10