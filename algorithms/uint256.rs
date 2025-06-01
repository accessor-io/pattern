impl Uint256 {
    pub fn from_u64(n: u64) -> Self {
        let mut ret = [0u64; 4];
        ret[3] = n;
        Uint256(ret)
    }
} 