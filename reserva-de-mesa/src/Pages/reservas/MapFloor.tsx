import { useLoader } from '@react-three/fiber'
import { TextureLoader, RepeatWrapping, Texture } from 'three'

type Props = {
  url?: string // caminho público, ex: '/map.jpg'
  width?: number // largura do plano em unidades do mundo
  height?: number // altura do plano em unidades do mundo
}

export default function MapFloor({ url = '/map.jpg', width = 26, height = 18 }: Props) {
  const originalTexture = useLoader(TextureLoader, url)
  let texture: Texture | null = null;
  if (originalTexture) {
    texture = originalTexture.clone();
    texture.wrapS = RepeatWrapping;
    texture.wrapT = RepeatWrapping;
    texture.repeat.set(1, 1);
    texture.flipY = false;
    texture.needsUpdate = true;
  }

  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[width, height]} />
      {texture && <meshStandardMaterial map={texture} />}
    </mesh>
  )
}