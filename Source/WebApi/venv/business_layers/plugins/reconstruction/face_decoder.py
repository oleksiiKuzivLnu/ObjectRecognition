import tensorflow as tf
import math as m
import numpy as np
from scipy.io import loadmat
import platform

is_windows = platform.system() == "Windows"

if not is_windows:
	from .renderer import mesh_renderer
###############################################################################################
# Reconstruct 3D face based on output coefficients and facemodel
###############################################################################################

# BFM 3D face model
class BFM():
	def __init__(self,model_path = './venv/business_layers/plugins/reconstruction/BFM/BFM_model_front.mat'):
		model = loadmat(model_path)
		self.meanshape = tf.compat.v1.constant(model['meanshape']) # mean face shape. [3*N,1]
		self.idBase = tf.compat.v1.constant(model['idBase']) # identity basis. [3*N,80]
		self.exBase = tf.compat.v1.constant(model['exBase'].astype(np.float32)) # expression basis. [3*N,64]
		self.meantex = tf.compat.v1.constant(model['meantex']) # mean face texture. [3*N,1] (0-255)
		self.texBase = tf.compat.v1.constant(model['texBase']) # texture basis. [3*N,80]
		self.point_buf = tf.compat.v1.constant(model['point_buf']) # face indices for each vertex that lies in. starts from 1. [N,8]
		self.face_buf = tf.compat.v1.constant(model['tri']) # vertex indices for each face. starts from 1. [F,3]
		self.front_mask_render = tf.compat.v1.squeeze(tf.compat.v1.constant(model['frontmask2_idx'])) # vertex indices for small face region to compute photometric error. starts from 1.
		self.mask_face_buf = tf.compat.v1.constant(model['tri_mask2']) # vertex indices for each face from small face region. starts from 1. [f,3]
		self.skin_mask = tf.compat.v1.squeeze(tf.compat.v1.constant(model['skinmask'])) # vertex indices for pre-defined skin region to compute reflectance loss
		self.keypoints = tf.compat.v1.squeeze(tf.compat.v1.constant(model['keypoints'])) # vertex indices for 68 landmarks. starts from 1. [68,1]

# Analytic 3D face
class Face3D():
	def __init__(self):
		facemodel = BFM()
		self.facemodel = facemodel

	# analytic 3D face reconstructions with coefficients from R-Net
	def Reconstruction_Block(self,coeff,opt):
		#coeff: [batchsize,257] reconstruction coefficients

		id_coeff,ex_coeff,tex_coeff,angles,translation,gamma,camera_scale,f_scale = self.Split_coeff(coeff)
		# [batchsize,N,3] canonical face shape in BFM space
		face_shape = self.Shape_formation_block(id_coeff,ex_coeff,self.facemodel)
		# [batchsize,N,3] vertex texture (in RGB order)
		face_texture = self.Texture_formation_block(tex_coeff,self.facemodel)
		# [batchsize,3,3] rotation matrix for face shape
		rotation = self.Compute_rotation_matrix(angles)
		# [batchsize,N,3] vertex normal
		face_norm = self.Compute_norm(face_shape,self.facemodel)
		norm_r = tf.compat.v1.matmul(face_norm,rotation)

		# do rigid transformation for face shape using predicted rotation and translation
		face_shape_t = self.Rigid_transform_block(face_shape,rotation,translation)
		# compute 2d landmark projections 
		# landmark_p: [batchsize,68,2]	
		face_landmark_t = self.Compute_landmark(face_shape_t,self.facemodel)
		landmark_p = self.Projection_block(face_landmark_t,camera_scale,f_scale)

		# [batchsize,N,3] vertex color (in RGB order)
		face_color = self.Illumination_block(face_texture, norm_r, gamma)

		# reconstruction images and region masks for computing photometric loss		
		render_imgs,img_mask,img_mask_crop = self.Render_block(face_shape_t,norm_r,face_color,camera_scale,f_scale,self.facemodel,opt.batch_size,opt.is_train)

		self.id_coeff = id_coeff
		self.ex_coeff = ex_coeff
		self.tex_coeff = tex_coeff
		self.f_scale = f_scale
		self.gamma = gamma
		self.face_shape = face_shape
		self.face_shape_t = face_shape_t
		self.face_texture = face_texture
		self.face_color = face_color
		self.landmark_p = landmark_p
		self.render_imgs = render_imgs
		self.img_mask = img_mask
		self.img_mask_crop = img_mask_crop

	#----------------------------------------------------------------------------------------------
	def Split_coeff(self,coeff):

		id_coeff = coeff[:,:80]
		ex_coeff = coeff[:,80:144]
		tex_coeff = coeff[:,144:224]
		angles = coeff[:,224:227]
		gamma = coeff[:,227:254]
		translation = coeff[:,254:257]
		camera_scale = tf.compat.v1.ones([tf.compat.v1.shape(coeff)[0],1])
		f_scale = tf.compat.v1.ones([tf.compat.v1.shape(coeff)[0],1])

		return id_coeff,ex_coeff,tex_coeff,angles,translation,gamma,camera_scale,f_scale

	def Shape_formation_block(self,id_coeff,ex_coeff,facemodel):
		face_shape = tf.compat.v1.einsum('ij,aj->ai',facemodel.idBase,id_coeff) + \
					tf.compat.v1.einsum('ij,aj->ai',facemodel.exBase,ex_coeff) + facemodel.meanshape

		# reshape face shape to [batchsize,N,3]
		face_shape = tf.compat.v1.reshape(face_shape,[tf.compat.v1.shape(face_shape)[0],-1,3])
		# re-centering the face shape with mean shape
		face_shape = face_shape - tf.compat.v1.reshape(tf.compat.v1.reduce_mean(tf.compat.v1.reshape(facemodel.meanshape,[-1,3]),0),[1,1,3])

		return face_shape

	def Compute_norm(self,face_shape,facemodel):
		shape = face_shape
		face_id = facemodel.face_buf
		point_id = facemodel.point_buf

		# face_id and point_id index starts from 1
		face_id = tf.compat.v1.cast(face_id - 1,tf.compat.v1.int32)
		point_id = tf.compat.v1.cast(point_id - 1,tf.compat.v1.int32)

		#compute normal for each face
		v1 = tf.compat.v1.gather(shape,face_id[:,0], axis = 1)
		v2 = tf.compat.v1.gather(shape,face_id[:,1], axis = 1)
		v3 = tf.compat.v1.gather(shape,face_id[:,2], axis = 1)
		e1 = v1 - v2
		e2 = v2 - v3
		face_norm = tf.compat.v1.cross(e1,e2)

		face_norm = tf.compat.v1.nn.l2_normalize(face_norm, dim = 2) # normalized face_norm first
		face_norm = tf.compat.v1.concat([face_norm,tf.compat.v1.zeros([tf.compat.v1.shape(face_shape)[0],1,3])], axis = 1)

		#compute normal for each vertex using one-ring neighborhood
		v_norm = tf.compat.v1.reduce_sum(tf.compat.v1.gather(face_norm, point_id, axis = 1), axis = 2)
		v_norm = tf.compat.v1.nn.l2_normalize(v_norm, dim = 2)
		
		return v_norm

	def Texture_formation_block(self,tex_coeff,facemodel):
		face_texture = tf.compat.v1.einsum('ij,aj->ai',facemodel.texBase,tex_coeff) + facemodel.meantex

		# reshape face texture to [batchsize,N,3], note that texture is in RGB order
		face_texture = tf.compat.v1.reshape(face_texture,[tf.compat.v1.shape(face_texture)[0],-1,3])

		return face_texture

	def Compute_rotation_matrix(self,angles):
		n_data = tf.compat.v1.shape(angles)[0]

		# compute rotation matrix for X-axis, Y-axis, Z-axis respectively
		rotation_X = tf.compat.v1.concat([tf.compat.v1.ones([n_data,1]),
			tf.compat.v1.zeros([n_data,3]),
			tf.compat.v1.reshape(tf.compat.v1.cos(angles[:,0]),[n_data,1]),
			-tf.compat.v1.reshape(tf.compat.v1.sin(angles[:,0]),[n_data,1]),
			tf.compat.v1.zeros([n_data,1]),
			tf.compat.v1.reshape(tf.compat.v1.sin(angles[:,0]),[n_data,1]),
			tf.compat.v1.reshape(tf.compat.v1.cos(angles[:,0]),[n_data,1])],
			axis = 1
			)

		rotation_Y = tf.compat.v1.concat([tf.compat.v1.reshape(tf.compat.v1.cos(angles[:,1]),[n_data,1]),
			tf.compat.v1.zeros([n_data,1]),
			tf.compat.v1.reshape(tf.compat.v1.sin(angles[:,1]),[n_data,1]),
			tf.compat.v1.zeros([n_data,1]),
			tf.compat.v1.ones([n_data,1]),
			tf.compat.v1.zeros([n_data,1]),
			-tf.compat.v1.reshape(tf.compat.v1.sin(angles[:,1]),[n_data,1]),
			tf.compat.v1.zeros([n_data,1]),
			tf.compat.v1.reshape(tf.compat.v1.cos(angles[:,1]),[n_data,1])],
			axis = 1
			)

		rotation_Z = tf.compat.v1.concat([tf.compat.v1.reshape(tf.compat.v1.cos(angles[:,2]),[n_data,1]),
			-tf.compat.v1.reshape(tf.compat.v1.sin(angles[:,2]),[n_data,1]),
			tf.compat.v1.zeros([n_data,1]),
			tf.compat.v1.reshape(tf.compat.v1.sin(angles[:,2]),[n_data,1]),
			tf.compat.v1.reshape(tf.compat.v1.cos(angles[:,2]),[n_data,1]),
			tf.compat.v1.zeros([n_data,3]),
			tf.compat.v1.ones([n_data,1])],
			axis = 1
			)

		rotation_X = tf.compat.v1.reshape(rotation_X,[n_data,3,3])
		rotation_Y = tf.compat.v1.reshape(rotation_Y,[n_data,3,3])
		rotation_Z = tf.compat.v1.reshape(rotation_Z,[n_data,3,3])

		# R = RzRyRx
		rotation = tf.compat.v1.matmul(tf.compat.v1.matmul(rotation_Z,rotation_Y),rotation_X)

		rotation = tf.compat.v1.transpose(rotation, perm = [0,2,1])

		return rotation

	def Projection_block(self,face_shape,camera_scale,f_scale):

		# pre-defined camera focal for pespective projection
		focal = tf.compat.v1.constant(1015.0)
		focal = focal*f_scale
		focal = tf.compat.v1.reshape(focal,[-1,1])
		batchsize = tf.compat.v1.shape(focal)[0]

		# define camera position
		camera_pos = tf.compat.v1.reshape(tf.compat.v1.constant([0.0,0.0,10.0]),[1,1,3])*tf.compat.v1.reshape(camera_scale,[-1,1,1])
		reverse_z = tf.compat.v1.tile(tf.compat.v1.reshape(tf.compat.v1.constant([1.0,0,0,0,1,0,0,0,-1.0]),[1,3,3]),[tf.compat.v1.shape(face_shape)[0],1,1])

		# compute projection matrix
		p_matrix = tf.compat.v1.concat([focal,tf.compat.v1.zeros([batchsize,1]),112.*tf.compat.v1.ones([batchsize,1]),tf.compat.v1.zeros([batchsize,1]),focal,112.*tf.compat.v1.ones([batchsize,1]),tf.compat.v1.zeros([batchsize,2]),tf.compat.v1.ones([batchsize,1])],axis = 1)
		p_matrix = tf.compat.v1.reshape(p_matrix,[-1,3,3])

		# convert z in world space to the distance to camera
		face_shape = tf.compat.v1.matmul(face_shape,reverse_z) + camera_pos
		aug_projection = tf.compat.v1.matmul(face_shape,tf.compat.v1.transpose(p_matrix,[0,2,1]))

		# [batchsize, N,2] 2d face projection
		face_projection = aug_projection[:,:,0:2]/tf.compat.v1.reshape(aug_projection[:,:,2],[tf.compat.v1.shape(face_shape)[0],tf.compat.v1.shape(aug_projection)[1],1])


		return face_projection


	def Compute_landmark(self,face_shape,facemodel):

		# compute 3D landmark postitions with pre-computed 3D face shape
		keypoints_idx = facemodel.keypoints
		keypoints_idx = tf.compat.v1.cast(keypoints_idx - 1,tf.compat.v1.int32)
		face_landmark = tf.compat.v1.gather(face_shape,keypoints_idx,axis = 1)

		return face_landmark

	def Illumination_block(self,face_texture,norm_r,gamma):
		n_data = tf.compat.v1.shape(gamma)[0]
		n_point = tf.compat.v1.shape(norm_r)[1]
		gamma = tf.compat.v1.reshape(gamma,[n_data,3,9])
		# set initial lighting with an ambient lighting
		init_lit = tf.compat.v1.constant([0.8,0,0,0,0,0,0,0,0])
		gamma = gamma + tf.compat.v1.reshape(init_lit,[1,1,9])

		# compute vertex color using SH function approximation
		a0 = m.pi 
		a1 = 2*m.pi/tf.compat.v1.sqrt(3.0)
		a2 = 2*m.pi/tf.compat.v1.sqrt(8.0)
		c0 = 1/tf.compat.v1.sqrt(4*m.pi)
		c1 = tf.compat.v1.sqrt(3.0)/tf.compat.v1.sqrt(4*m.pi)
		c2 = 3*tf.compat.v1.sqrt(5.0)/tf.compat.v1.sqrt(12*m.pi)

		Y = tf.compat.v1.concat([tf.compat.v1.tile(tf.compat.v1.reshape(a0*c0,[1,1,1]),[n_data,n_point,1]),
			tf.compat.v1.expand_dims(-a1*c1*norm_r[:,:,1],2),
			tf.compat.v1.expand_dims(a1*c1*norm_r[:,:,2],2),
			tf.compat.v1.expand_dims(-a1*c1*norm_r[:,:,0],2),
			tf.compat.v1.expand_dims(a2*c2*norm_r[:,:,0]*norm_r[:,:,1],2),
			tf.compat.v1.expand_dims(-a2*c2*norm_r[:,:,1]*norm_r[:,:,2],2),
			tf.compat.v1.expand_dims(a2*c2*0.5/tf.compat.v1.sqrt(3.0)*(3*tf.compat.v1.square(norm_r[:,:,2])-1),2),
			tf.compat.v1.expand_dims(-a2*c2*norm_r[:,:,0]*norm_r[:,:,2],2),
			tf.compat.v1.expand_dims(a2*c2*0.5*(tf.compat.v1.square(norm_r[:,:,0])-tf.compat.v1.square(norm_r[:,:,1])),2)],axis = 2)

		color_r = tf.compat.v1.squeeze(tf.compat.v1.matmul(Y,tf.compat.v1.expand_dims(gamma[:,0,:],2)),axis = 2)
		color_g = tf.compat.v1.squeeze(tf.compat.v1.matmul(Y,tf.compat.v1.expand_dims(gamma[:,1,:],2)),axis = 2)
		color_b = tf.compat.v1.squeeze(tf.compat.v1.matmul(Y,tf.compat.v1.expand_dims(gamma[:,2,:],2)),axis = 2)

		#[batchsize,N,3] vertex color in RGB order
		face_color = tf.compat.v1.stack([color_r*face_texture[:,:,0],color_g*face_texture[:,:,1],color_b*face_texture[:,:,2]],axis = 2)

		return face_color

	def Rigid_transform_block(self,face_shape,rotation,translation):
		# do rigid transformation for 3D face shape
		face_shape_r = tf.compat.v1.matmul(face_shape,rotation)
		face_shape_t = face_shape_r + tf.compat.v1.reshape(translation,[tf.compat.v1.shape(face_shape)[0],1,3])

		return face_shape_t

	def Render_block(self,face_shape,face_norm,face_color,camera_scale,f_scale,facemodel,batchsize,is_train=True):
		if is_train and is_windows:
			raise ValueError('Not support training with Windows environment.')

		if is_windows:
			return [],[],[]

		# render reconstruction images 
		n_vex = int(facemodel.idBase.shape[0].value/3)
		fov_y = 2*tf.compat.v1.atan(112./(1015.*f_scale))*180./m.pi
		fov_y = tf.compat.v1.reshape(fov_y,[batchsize])
		# full face region
		face_shape = tf.compat.v1.reshape(face_shape,[batchsize,n_vex,3])
		face_norm = tf.compat.v1.reshape(face_norm,[batchsize,n_vex,3])
		face_color = tf.compat.v1.reshape(face_color,[batchsize,n_vex,3])

		# pre-defined cropped face region
		mask_face_shape = tf.compat.v1.gather(face_shape,tf.compat.v1.cast(facemodel.front_mask_render-1,tf.compat.v1.int32),axis = 1)
		mask_face_norm = tf.compat.v1.gather(face_norm,tf.compat.v1.cast(facemodel.front_mask_render-1,tf.compat.v1.int32),axis = 1)
		mask_face_color = tf.compat.v1.gather(face_color,tf.compat.v1.cast(facemodel.front_mask_render-1,tf.compat.v1.int32),axis = 1)

		# setting cammera settings
		camera_position = tf.compat.v1.constant([[0,0,10.0]])*tf.compat.v1.reshape(camera_scale,[-1,1])
		camera_lookat = tf.compat.v1.constant([0,0,0.0])
		camera_up = tf.compat.v1.constant([0,1.0,0])

		# setting light source position(intensities are set to 0 because we have computed the vertex color)
		light_positions = tf.compat.v1.tile(tf.compat.v1.reshape(tf.compat.v1.constant([0,0,1e5]),[1,1,3]),[batchsize,1,1])
		light_intensities = tf.compat.v1.tile(tf.compat.v1.reshape(tf.compat.v1.constant([0.0,0.0,0.0]),[1,1,3]),[batchsize,1,1])
		ambient_color = tf.compat.v1.tile(tf.compat.v1.reshape(tf.compat.v1.constant([1.0,1,1]),[1,3]),[batchsize,1])

		#using tf_mesh_renderer for rasterization (https://github.com/google/tf_mesh_renderer)
		# img: [batchsize,224,224,3] images in RGB order (0-255)
		# mask:[batchsize,224,224,1] transparency for img ({0,1} value)
		with tf.compat.v1.device('/cpu:0'):
			img_rgba = mesh_renderer.mesh_renderer(face_shape,
				tf.compat.v1.cast(facemodel.face_buf-1,tf.compat.v1.int32),
				face_norm,
				face_color,
				camera_position = camera_position,
				camera_lookat = camera_lookat,
				camera_up = camera_up,
				light_positions = light_positions,
				light_intensities = light_intensities,
				image_width = 224,
				image_height = 224,
				fov_y = fov_y,
				near_clip = 0.01,
				far_clip = 50.0,
				ambient_color = ambient_color)

		img = img_rgba[:,:,:,:3]
		mask = img_rgba[:,:,:,3:]

		img = tf.compat.v1.cast(img[:,:,:,::-1],tf.compat.v1.float32) #transfer RGB to BGR
		mask = tf.compat.v1.cast(mask,tf.compat.v1.float32) # full face region

		if is_train:
			# compute mask for small face region
			with tf.compat.v1.device('/cpu:0'):
				img_crop_rgba = mesh_renderer.mesh_renderer(mask_face_shape,
					tf.compat.v1.cast(facemodel.mask_face_buf-1,tf.compat.v1.int32),
					mask_face_norm,
					mask_face_color,
					camera_position = camera_position,
					camera_lookat = camera_lookat,
					camera_up = camera_up,
					light_positions = light_positions,
					light_intensities = light_intensities,
					image_width = 224,
					image_height = 224,
					fov_y = fov_y,
					near_clip = 0.01,
					far_clip = 50.0,
					ambient_color = ambient_color)

			mask_f = img_crop_rgba[:,:,:,3:]
			mask_f = tf.compat.v1.cast(mask_f,tf.compat.v1.float32) # small face region
			return img,mask,mask_f

		img_rgba = tf.compat.v1.cast(tf.compat.v1.clip_by_value(img_rgba,0,255),tf.compat.v1.float32)

		return img_rgba,mask,mask
