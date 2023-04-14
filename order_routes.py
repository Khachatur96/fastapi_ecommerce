from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel
from fastapi.exceptions import HTTPException
from database import Session, engine
from fastapi.encoders import jsonable_encoder

from utills import authorization_required

session = Session(bind=engine)

order_router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)


@order_router.get('/')
async def hello(authorize: AuthJWT = Depends()):
    authorization_required(authorize)
    return {"message": "hello, world!"}


@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, authorize: AuthJWT = Depends()):
    authorization_required(authorize)

    current_user = authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity
    )
    new_order.user = user
    session.add(new_order)
    session.commit()

    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }
    return jsonable_encoder(response)


@order_router.get('/orders')
async def list_all_orders(authorize: AuthJWT = Depends()):
    authorization_required(authorize)
    current_user = authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not superuser"
        )
    orders = session.query(Order).all()
    return jsonable_encoder(orders)


@order_router.get('/orders/{id}')
async def get_order_by_id(id: int, authorize: AuthJWT = Depends()):
    authorization_required(authorize)
    current_user = authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            return jsonable_encoder(order)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="order with specified id does not exists"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not allowed to carry out request"
        )


@order_router.get('/user_orders')
async def get_user_orders(authorize: AuthJWT = Depends()):
    authorization_required(authorize)
    current_user = authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    return jsonable_encoder(user.orders)


@order_router.get('/user/order/{order_id}/')
async def get_user_orders(order_id: int, authorize: AuthJWT = Depends()):
    authorization_required(authorize)
    current_user = authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    orders = user.orders

    for order in orders:
        if order.id == order_id:
            return order
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="No order with such id"
    )


@order_router.put('/orders/update/{order_id}')
async def get_order_by_id(order_id: int, obj: OrderModel, authorize: AuthJWT = Depends()):
    authorization_required(authorize)
    order = session.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.quantity = obj.quantity
    order.pizza_size = obj.pizza_size
    session.commit()
    return jsonable_encoder(order)
