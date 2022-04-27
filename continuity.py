class Continuity:
    """A class that contains information about the continuity between two geometries and defines which of two continuities is lower or higher when compared with a comparison operator (<, >, ==, etc.)."""

    def __init__(self, type: str = None, order: int = None):
        if type is not None and order is not None:
            assert type in ('C', 'G', 'CG'), f"Invalid continuity type {type}."
            assert not (order > 0 and type == 'CG'), f"Invalid continuity type {type} for order greater than 0."
        self.order = order
        self.type = type
    
    def __bool__(self) -> bool:
        """Return True if continuity exists."""
        return self.type is not None and self.order is not None
    
    def __eq__(self, continuity) -> bool:
        """Return True if this object has the same continuity as the one given."""
        if self and continuity:
            # C0 and G0 are equivalent.
            if self.order == 0 and continuity.order == 0:
                return True
            # At orders above 0, C is higher than G, and the two are not equivalent.
            else:
                return self.order == continuity.order and self.type == continuity.type
        else:
            return False
    
    def __lt__(self, continuity) -> bool:
        """Return True if this object has continuity less than the one given."""
        if self and continuity:
            return (
                (self.order < continuity.order or self.type == 'G' and continuity.type == 'C') and
                self != continuity
            )
        else:
            return False
    
    def __le__(self, continuity) -> bool:
        """Return True if this object has continuity less than or equal to the one given."""
        return self < continuity or self == continuity
    
    def __repr__(self) -> str:
        if self:
            if self.order == 0:
                return "/".join([f"{type}{self.order}" for type in self.type])
            else:
                return f"{self.type}{self.order}"
        else:
            return "no"