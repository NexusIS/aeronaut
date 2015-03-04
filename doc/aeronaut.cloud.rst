aeronaut.cloud module
---------------------

Provides methods and classes to connect and interact with a DiData Cloud
Server provider. See :func:`~aeronaut.cloud.connect` for information on
how to establish a connection.

.. automodule:: aeronaut.cloud
    :undoc-members:
    :show-inheritance:

    .. autofunction:: connect

    .. autoclass:: CloudConnection
        :members:

    .. autoexception:: AuthenticationError
        :members:

    .. autoexception:: NotAuthenticatedError
        :members:

    .. autoexception:: OperationForbiddenError
        :members:

    .. autoexception:: UnauthorizedError
        :members:
