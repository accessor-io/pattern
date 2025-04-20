// Update macro to handle primitive types
macro_rules! impl_serializable {
    ($name:ident, $($field:ident),+) => {
        impl Serializable for $name {
            fn serialize(&self, writer: &mut dyn Write) -> Result<()> {
                $(self.$field.serialize(writer)?;)+
                Ok(())
            }
        }
    };
} 