def db_drop():
    from core import Base
    from core.Status import Status
    from core.Test import Test
    from core.Index import Index
    from core.TestType import TestType
    Base.Base().get_base()[Status.collection].drop()
    Base.Base().get_base()[Test.collection].drop()
    Base.Base().get_base()[Index.collection].drop()
    Base.Base().get_base()[TestType.collection].drop()
