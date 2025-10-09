#!/usr/bin/env python3
"""
Dynamic Learner - Ingests new knowledge into Jade's RAG system
Watches intake/ directory and automatically processes new files
"""

import sys
from pathlib import Path
import shutil
from datetime import datetime

# Add GP-DATA to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "GP-DATA"))

try:
    from simple_sync import sync_directory_to_chroma
    HAS_SYNC = True
except ImportError:
    HAS_SYNC = False
    print("⚠️  simple_sync not available - install dependencies")

class DynamicLearner:
    """Ingests new knowledge from intake/ into ChromaDB"""
    
    def __init__(self):
        self.gp_rag_root = Path(__file__).parent.parent
        self.intake_dir = self.gp_rag_root / "intake"
        self.processed_dir = self.gp_rag_root / "processed"
        self.failed_dir = self.gp_rag_root / "failed"
        
        # Ensure directories exist
        self.intake_dir.mkdir(exist_ok=True)
        self.processed_dir.mkdir(exist_ok=True)
        self.failed_dir.mkdir(exist_ok=True)
    
    def learn_all(self):
        """Process all files in intake/"""
        total_files = 0
        successful = 0
        
        print(f"🔍 Scanning {self.intake_dir}...")
        
        # Find all markdown/text files
        for category_dir in self.intake_dir.iterdir():
            if not category_dir.is_dir():
                continue
                
            for file_path in category_dir.glob("*"):
                if file_path.suffix in ['.md', '.txt', '.json', '.yaml', '.yml']:
                    total_files += 1
                    if self.learn_file(file_path, category=category_dir.name):
                        successful += 1
        
        print(f"\n✅ Processed {successful}/{total_files} files")
        return successful
    
    def learn_file(self, file_path: Path, category: str = "general"):
        """Learn a single file"""
        print(f"📖 Learning: {file_path.name}")
        
        try:
            if not HAS_SYNC:
                print("   ⚠️  Skipping - simple_sync not available")
                return False
            
            # Read content
            content = file_path.read_text()
            
            # Sync to ChromaDB
            collection_name = f"{category}_knowledge"
            sync_directory_to_chroma(
                str(file_path.parent),
                collection_name=collection_name
            )
            
            # Move to processed
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_subdir = self.processed_dir / timestamp
            processed_subdir.mkdir(exist_ok=True)
            
            dest = processed_subdir / file_path.name
            shutil.move(str(file_path), str(dest))
            
            print(f"   ✅ Learned and moved to processed/{timestamp}/")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            
            # Move to failed with error log
            failed_dest = self.failed_dir / file_path.name
            error_log = self.failed_dir / f"{file_path.name}.error.log"
            
            shutil.move(str(file_path), str(failed_dest))
            error_log.write_text(f"Error: {e}\nFile: {file_path}\nTimestamp: {datetime.now()}")
            
            return False

def main():
    """CLI entry point"""
    learner = DynamicLearner()
    count = learner.learn_all()
    print(f"\n🎓 Total knowledge chunks learned: {count}")

if __name__ == "__main__":
    main()
