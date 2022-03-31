# Poslito Websocket Service API 1.0.0 documentation

* Email support: [leontiev.oliver@gmail.com](mailto:leontiev.oliver@gmail.com)

[Find more info here.](https://github.com/revilO602/BP-API)

Websocket service for tracking courier positions.


## Table of Contents

* [Servers](#servers)
  * [public](#public-server)
* [Operations](#operations)
  * [PUB /couriers](#pub-couriers-operation)
  * [SUB /couriers](#sub-couriers-operation)
  * [PUB /couriers/{deliveryId}](#pub-couriersdeliveryid-operation)
  * [SUB /couriers/{deliveryId}](#sub-couriersdeliveryid-operation)

## Servers

### `public` Server

* URL: `wss://poslito.com/ws`
* Protocol: `wss`



## Operations

### PUB `/couriers` Operation

*Send current position to all subscribers. Only authenticated courier can publish.*

#### `ws` Channel specific information

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| query | string | Query parameters e.g. /?token=someuuid | - | - | - |
| query.token | string | JWT access token of the courier. Required to send position over the websocket. | - | - | - |

#### Message `CourierPosition`

*Geographical coordinates of the courier.*

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | - | - | - | **additional properties are allowed** |
| latitude | number | - | - | format (`float`), [ -90 .. 90 ] | - |
| longitude | number | - | - | format (`float`), [ -180 .. 180 ] | - |

> Examples of payload

```json
{
  "latitude": 50.6548,
  "longitude": 62.2415
}
```



### SUB `/couriers` Operation

*Receive current position of all publishing couriers. No authentication needed.*

#### `ws` Channel specific information

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| query | string | Query parameters e.g. /?token=someuuid | - | - | - |
| query.token | string | JWT access token of the courier. Required to send position over the websocket. | - | - | - |

#### Message `CourierPositionWithCourierId`

*Geographical coordinates of the courier with the couriers unique ID.*

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | allOf | - | - | - | **additional properties are allowed** |
| 0 (allOf item) | object | - | - | - | **additional properties are allowed** |
| latitude | number | - | - | format (`float`), [ -90 .. 90 ] | - |
| longitude | number | - | - | format (`float`), [ -180 .. 180 ] | - |
| 1 (allOf item) | object | - | - | - | **additional properties are allowed** |
| 1.courier_id | string | - | - | format (`uuid`) | - |

> Examples of payload _(generated)_

```json
{
  "latitude": -90,
  "longitude": -180,
  "courier_id": "e5eb1b54-d6fe-4c0e-9ed7-ae2f5edcf2d5"
}
```



### PUB `/couriers/{deliveryId}` Operation

*Send current position to all subscribers. Only courier assigned to the delivery can publish.*

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| deliveryId | string | Id of the delivery assigned to the courier. | - | format (`uuid`) | **required** |


#### `ws` Channel specific information

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| query | string | Query parameters e.g. /?token=someuuid | - | - | - |
| query.token | string | JWT access token of the courier. Required to send position over the websocket. | - | - | - |

#### Message `CourierPosition`

*Geographical coordinates of the courier.*

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | object | - | - | - | **additional properties are allowed** |
| latitude | number | - | - | format (`float`), [ -90 .. 90 ] | - |
| longitude | number | - | - | format (`float`), [ -180 .. 180 ] | - |

> Examples of payload

```json
{
  "latitude": 50.6548,
  "longitude": 62.2415
}
```



### SUB `/couriers/{deliveryId}` Operation

*Receive current position of courier. Anyone who knows the correct id of the delivery can subscribe. No authentication needed.*

#### Parameters

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| deliveryId | string | Id of the delivery assigned to the courier. | - | format (`uuid`) | **required** |


#### `ws` Channel specific information

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| query | string | Query parameters e.g. /?token=someuuid | - | - | - |
| query.token | string | JWT access token of the courier. Required to send position over the websocket. | - | - | - |

#### Message `CourierPositionWithCourierId`

*Geographical coordinates of the courier with the couriers unique ID.*

##### Payload

| Name | Type | Description | Value | Constraints | Notes |
|---|---|---|---|---|---|
| (root) | allOf | - | - | - | **additional properties are allowed** |
| 0 (allOf item) | object | - | - | - | **additional properties are allowed** |
| latitude | number | - | - | format (`float`), [ -90 .. 90 ] | - |
| longitude | number | - | - | format (`float`), [ -180 .. 180 ] | - |
| 1 (allOf item) | object | - | - | - | **additional properties are allowed** |
| 1.courier_id | string | - | - | format (`uuid`) | - |

> Examples of payload _(generated)_

```json
{
  "latitude": -90,
  "longitude": -180,
  "courier_id": "e5eb1b54-d6fe-4c0e-9ed7-ae2f5edcf2d5"
}
```



