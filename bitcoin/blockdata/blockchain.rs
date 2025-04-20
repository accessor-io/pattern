impl Hash for BlockchainNode {
    fn hash(&self) -> Sha256dHash {
        Sha256dHash::hash(&self.header)
    }
} 