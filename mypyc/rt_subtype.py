"""*Runtime* Subtype check for RTypes."""

from mypyc.ops import (
    RType, ROptional, RInstance, RPrimitive, RTuple, RVoid, RTypeVisitor,
    is_bool_rprimitive, is_int_rprimitive, is_tuple_rprimitive, none_rprimitive,
    is_unsafe_int_rprimitive,
    is_object_rprimitive
)
from mypyc.sametype import is_same_type
from mypyc.subtype import is_subtype


def is_runtime_subtype(left: RType, right: RType) -> bool:
    if not left.is_unboxed and is_object_rprimitive(right):
        return True
    return left.accept(RTSubtypeVisitor(right))


class RTSubtypeVisitor(RTypeVisitor[bool]):
    """Is left a runtime subtype of right?

    A few special cases such as right being 'object' are handled in
    is_subtype and don't need to be covered here.
    """

    def __init__(self, right: RType) -> None:
        self.right = right

    def visit_rinstance(self, left: RInstance) -> bool:
        return isinstance(self.right, RInstance) and is_subtype(left, self.right)

    def visit_roptional(self, left: ROptional) -> bool:
        # XXX
        return isinstance(self.right, ROptional) and is_subtype(left.value_type,
                                                                self.right.value_type)

    def visit_rprimitive(self, left: RPrimitive) -> bool:
        if is_unsafe_int_rprimitive(left) and is_int_rprimitive(self.right):
            return True
        return isinstance(self.right, RPrimitive) and left.name == self.right.name

    def visit_rtuple(self, left: RTuple) -> bool:
        return is_same_type(left, self.right)
        # if isinstance(self.right, RTuple):
        #     return len(self.right.types) == len(left.types) and all(
        #         is_runtime_subtype(t1, t2) for t1, t2 in zip(left.types, self.right.types))
        # return False

    def visit_rvoid(self, left: RVoid) -> bool:
        return isinstance(self.right, RVoid)
