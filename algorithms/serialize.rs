pub trait Serializable {
    fn serialize(&self, writer: &mut dyn Write) -> Result<()>;
    
    // Add default implementation for serialize_iter
    fn serialize_iter<'a>(&'a self) -> Box<dyn Iterator<Item = u8> + 'a> {
        let mut vec = Vec::new();
        self.serialize(&mut vec).unwrap();
        Box::new(vec.into_iter())
    }
} 