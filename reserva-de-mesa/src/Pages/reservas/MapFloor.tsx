import React, { useEffect, useMemo } from 'react'
import { useLoader } from '@react-three/fiber'
import type { ThreeEvent } from '@react-three/fiber'
import { TextureLoader, RepeatWrapping, Texture } from 'three'
import type { Vector3 } from 'three'

type Props = {
  url?: string
  width?: number
  height?: number
  onMapClick?: (pos: { x: number; y: number; z: number }) => void
}

/**
 * MapFloor - desenha o plano com a textura do mapa e
 * envia a posição world (x,y,z) quando o usuário clica sobre o plano.
 *
 * NOTE: não modifica a textura retornada por useLoader — clona antes.
 */
const MapFloor: React.FC<Props> = ({ url = '/map.jpg', width = 26, height = 18, onMapClick }) => {
  // textura "original" (não modificaremos ela)
  const originalTexture = useLoader(TextureLoader, url)

  // clonamos a textura e modificamos o clone (safe)
  const texture = useMemo((): Texture | null => {
    if (!originalTexture) return null
    const t = originalTexture.clone()
    t.wrapS = RepeatWrapping
    t.wrapT = RepeatWrapping
    t.repeat.set(1, 1)
    t.flipY = false
    t.needsUpdate = true
    return t
  }, [originalTexture])

  // limpar/dispose do clone quando o componente desmontar
  useEffect(() => {
    return () => {
      if (texture) {
        texture.dispose()
      }
    }
  }, [texture])

  if (!texture) return null

  return (
    <mesh
      rotation={[-Math.PI / 2, 0, 0]}
      receiveShadow
      onPointerDown={(e: ThreeEvent<PointerEvent>) => {
        e.stopPropagation()
        const p: Vector3 = e.point
        if (onMapClick) onMapClick({ x: p.x, y: p.y, z: p.z })
      }}
    >
      <planeGeometry args={[width, height]} />
      <meshStandardMaterial map={texture} />
    </mesh>
  )
}

export default MapFloor