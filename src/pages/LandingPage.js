import React, { useRef, useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { useNavigate } from 'react-router-dom';
import { OrbitControls } from '@react-three/drei';
import { gsap } from 'gsap';
import { Typography } from '@mui/material';

function Logo({ onLogoClick }) {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);

  useEffect(() => {
    if (meshRef.current) {
      gsap.to(meshRef.current.rotation, {
        y: Math.PI * 2,
        duration: 10,
        repeat: -1,
        ease: "none"
      });
    }
  }, []);

  useEffect(() => {
    if (meshRef.current) {
      gsap.to(meshRef.current.scale, {
        x: hovered ? 1.2 : 1,
        y: hovered ? 1.2 : 1,
        z: hovered ? 1.2 : 1,
        duration: 0.3
      });
    }
  }, [hovered]);

  return (
    <mesh
      ref={meshRef}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
      onClick={onLogoClick}
    >
      <boxGeometry args={[1.5, 1.5, 1.5]} />
      <meshStandardMaterial color={hovered ? "#2196F3" : "#00BCD4"} />
    </mesh>
  );
}

function LandingPage() {
  const navigate = useNavigate();
  const [clicked, setClicked] = useState(false);

  const handleLogoClick = () => {
    setClicked(true);
    gsap.to('.landing-content', {
      opacity: 0,
      duration: 1,
      onComplete: () => {
        navigate('/dashboard');
      }
    });
  };

  return (
    <div className="landing-content" style={{
      width: '100vw',
      height: '100vh',
      background: 'linear-gradient(135deg, #00BCD4 0%, #2196F3 100%)',
      position: 'relative',
    }}>
      <Canvas
        camera={{ position: [0, 0, 5] }}
        style={{
          width: '100%',
          height: '60%',
          position: 'absolute',
          top: '20%'
        }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <Logo onLogoClick={handleLogoClick} />
        <OrbitControls
          enableZoom={false}
          enablePan={false}
          autoRotate={true}
          autoRotateSpeed={1}
        />
      </Canvas>
      <div style={{
        position: 'absolute',
        bottom: '15%',
        left: '50%',
        transform: 'translateX(-50%)',
        color: 'white',
        textAlign: 'center',
        width: '100%',
        maxWidth: '600px',
      }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 500,
            letterSpacing: '0.2rem',
            textShadow: '2px 2px 4px rgba(0,0,0,0.2)',
            mb: 1
          }}
        >
          SYNCRUIT
        </Typography>
        <Typography
          variant="subtitle1"
          sx={{
            fontWeight: 300,
            letterSpacing: '0.1rem',
            textShadow: '1px 1px 2px rgba(0,0,0,0.1)',
            mb: 2,
            opacity: 0.9
          }}
        >
          WHERE TALENT MEETS ITS MATCH
        </Typography>
        <Typography
          variant="body2"
          sx={{
            opacity: 0.7,
            fontSize: '0.9rem'
          }}
        >
          Click the cube to begin
        </Typography>
      </div>
    </div>
  );
}

export default LandingPage;
