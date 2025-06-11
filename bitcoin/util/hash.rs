#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct Sha256dHash([u8; 32]);

impl Sha256dHash {
    pub fn hash<T: Serializable>(data: &T) -> Self {
        let mut engine = Sha256d::new();
        data.serialize(&mut engine).unwrap();
        Sha256dHash(engine.finish())
    }
} 